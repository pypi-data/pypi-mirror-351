import json
import pathlib
import re
import urllib.request
from .row_result import RowResult

# RF constants are the names of fields in the Solr response
RF_FILE_ID = "file_id_num"
RF_SIZE = "file_premis_size_num"
RF_ROLE = "file_huldrsadmin_role_string"
RF_FILE_NAME = "file_huldrsadmin_suppliedFilename_string"
RF_ACCESS_FLAG = "file_huldrsadmin_accessFlag_string"
RF_URI_STRING = "file_huldrsadmin_uri_string"

# We want all these fields in the response to our file sizes query.
RESPONSE_FIELDS = [
    RF_FILE_ID,
    RF_SIZE,
    RF_ROLE,
    RF_FILE_NAME,
    RF_ACCESS_FLAG,
    RF_URI_STRING,
]


class SolrClient:
    """
    A simple Solr client that can return object ids and URNs from
    an http or https gateway that ultimately queries the Solr
    database at libsearch8elb-prod.lib.harvard.edu.

    See https://github.huit.harvard.edu/LTS/fal-small-images-gateway
    for details on the gateway.
    """

    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url.rstrip('/')
        self.result: RowResult = None

    def process_row(self, row_number: int, urns: list[str]) -> RowResult:
        """
        Process one row from the CSV input file: look up the URNs from
        that row in Solr and see if we can find a larger deliverable image.
        """
        self.result = RowResult(row_number, urns)
        if not self.result.filename_present():
            self.result.skipped_because = "Row has no filename"
            return self.result
        image = self.largest_deliverable_for_file(urns)
        if image is not None:
            self.result.found_deliverable_images = True
            self.result.set_largest_image(image)
        return self.result

    def obj_id_query_url(self, urn_list: list[str]) -> str:
        """
        Returns the URL to retrieve object ids associated with the specified
        URNs. Note that this calls prepare_urns() to strip off "DRS:" prefixes
        from the URNs.
        """
        query_params = ""
        for urn in self.normalize_urns(urn_list):
            query_params += f"urns={urn}&"
        return f"{self.gateway_url}/api/get_object_ids?{query_params}"

    def file_size_query_url(self, obj_id: int) -> str:
        """
        Returns a URL for retrieving files info (including file sizes) for
        images related to the specified object ID.
        """
        return f"{self.gateway_url}/api/get_image_list?id={obj_id}"

    def normalize_urns(self, urn_list: list[str]) -> list[str]:
        """
        Prepares URNs found in the CSV file for use in querying Solr.
        This means stripping off the "DRS:" prefix, if present, and
        capitalizing all of the URN string that comes after the "urn-3:"
        prefix.
        """
        stripped_uc_urns = [
            re.sub(r"^DRS:", "", urn.upper()) for urn in urn_list
        ]
        return [re.sub(r"^URN-3:", "urn-3:", urn) for urn in stripped_uc_urns]

    def get_object_ids(self, file_urns: str) -> set[int]:
        """
        Returns the object IDs associated with a list of file URNs.
        Note that the file_urns param is a single string containing a
        comma-separated list of values.
        E.g. "drs:urn-3:fhcl:164995,urn-3:fhcl:124938"
        """
        url = self.obj_id_query_url(file_urns)
        json_str = self._request_data(url)
        data = json.loads(json_str)
        obj_ids = set()
        for doc in data["response"]["docs"]:
            obj_ids.add(doc["object_id_num"])
        return obj_ids

    def get_image_list(self, obj_id: int):
        """
        Returns a list of images from Solr that are related to the specified
        object ID.
        """
        url = self.file_size_query_url(obj_id)
        json_str = self._request_data(url)
        data = json.loads(json_str)
        return data["response"]["docs"]

    def _request_data(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            json_str = response.read().decode('utf-8')
        return json_str

    def largest_deliverable_in_list(
        self, image_list: list[dict[str, any]]
    ) -> dict | None:
        """
        Given a list of images from get_image_list(), this returns the
        largest deliverable image with public or restricted access.
        """
        largest_deliverable = 0
        winner = None
        normalized_urns = self.normalize_urns(self.result.original_urns)
        for image in image_list:
            if not image.get(RF_URI_STRING):
                continue
            size = image.get(RF_SIZE, 0)
            if image.get(RF_URI_STRING)[0] in normalized_urns:
                # TODO: We can't always assume this is the thumbnail
                self.result.original_thumbnail_size = size
            if self.is_deliverable_candidate(image):
                if size > largest_deliverable:
                    largest_deliverable = size
                    winner = image
        return winner

    def is_deliverable_candidate(self, image: dict[str, any]) -> bool:
        """
        Returns true if image has "deliverable" role and "P" or "R" access
        and is not a jp2 file. Param image is a dict retrieved from Solr.
        """
        role = image.get(RF_ROLE)
        access = image.get(RF_ACCESS_FLAG, "").upper()
        file_name = image.get(RF_FILE_NAME)
        if file_name and pathlib.Path(file_name).suffix.upper() == ".JP2":
            return False
        if not role or "DELIVERABLE" not in role:
            return False
        if not access == "P" and not access == "R":
            return False
        return True

    def largest_deliverable_for_file(self, urn_list: list[str]) -> dict | None:
        """
        Returns the largest deliverable file associated with the specified
        URN list, or None. The returned object is a dict containing the
        keys listed in RESPONSE_FIELDS.
        """
        obj_ids = self.get_object_ids(urn_list)
        if len(obj_ids) < 1:
            self.result.error = "Object id not found."
            return None
        elif len(obj_ids) > 1:
            self.result.error = f"Multiple object ids: {obj_ids}"
            return None
        image_list = self.get_image_list(list(obj_ids)[0])
        largest = self.largest_deliverable_in_list(image_list)
        return largest
