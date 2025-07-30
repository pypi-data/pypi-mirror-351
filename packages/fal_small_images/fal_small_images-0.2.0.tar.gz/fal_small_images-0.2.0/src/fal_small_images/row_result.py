class RowResult:
    """
    RowResult captures info about the result of processing one row
    from the input CSV file.
    """

    def __init__(self, row_number: int, original_urns: list[str]):
        """
        Creates a new row result. Param row_number is the number of
        the row from the input CSV file. Param original_urns is a
        list of URNs found in the Filename column of the input row.
        The URNs appear in the file as a comma-delimited string.
        Split the string to create original_urns before calling this.
        """
        self.row_number: int = row_number

        self.original_urns: list[str] = original_urns
        self.original_urn_count: int = len(original_urns)
        self.original_large_urn: str = ""
        self.original_large_size: int = 0
        self.original_thumbnail_urn: str = ""
        self.original_thumbnail_size: int = 0

        self.updated_large_urn: str = ""
        self.updated_large_size: int = 0
        self.updated_thumbnail_urn: str = ""
        self.updated_thumbnail_size: int = 0

        self.skipped_because: str | None = None
        self.found_deliverable_images: bool = False
        self.error: str = None

    def filename_present(self) -> bool:
        """
        Returns true if this struct has one or more original_urns.
        Those are passed into the constructor from the input CSV
        file.
        """
        if not self.original_urns:
            self.skipped_because = "Record has no filename"
            return False
        return True

    def skipped(self) -> bool:
        """
        Returns true if we skipped processing for this row in
        the CSV file.
        """
        return self.skipped_because is not None

    def set_largest_image(self, image: dict[str, any]) -> bool:
        """
        Sets self.updated_large_urn and self.updated_large_size
        to the urn and size of the image param you pass in.
        """
        largest_urn = None
        if self.original_urn_count > 1:
            largest_urn = self.original_urns[1]

        new_largest_urn = image["file_huldrsadmin_uri_string"][0]
        new_largest_size = image["file_premis_size_num"]
        if not largest_urn or largest_urn != new_largest_urn:
            self.updated_large_urn = new_largest_urn
            self.updated_large_size = new_largest_size

    def found_larger_image(self) -> bool:
        """
        Returns true if our Solr search yielded a larger image than
        the one found in the input CSV file.
        """
        # Force the formatting of the Solr URNs to match the formatting
        # of the input spreadsheet's URNs so we get a valid comparison.
        denormalized_updated_urns = [
            self.updated_large_urn.lower(),
            "drs:" + self.updated_large_urn.lower(),
        ]
        overlap = list(
            set(denormalized_updated_urns) & set(self.original_urns)
        )
        return len(overlap) == 0

    def get_output_urns(self) -> str:
        """
        Returns the URN or URNs to be printed to the Filename column
        of the output CSV file. This includes the original thumbnail
        URL (which usually has the 'drs:' prefix) and the URN for the
        larger image (no 'drs:' prefix). If there are two URNs, they
        will be returned as a single comma-delimited string.
        """
        if self.original_urn_count == 0:
            return ""
        urns = self.original_urns
        if self.found_larger_image():
            larger_urn = self.updated_large_urn.lower()
            if self.original_urn_count == 1:
                urns = [larger_urn]
            else:
                urns = [self.original_urns[0], larger_urn]
        return ",".join(urns)
