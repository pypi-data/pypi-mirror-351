import json
import pytest
from unittest.mock import patch, MagicMock
from fal_small_images.solr_client import (
    SolrClient,
    RF_FILE_ID,
    RF_SIZE,
    RF_ROLE,
    RF_FILE_NAME,
    RF_ACCESS_FLAG,
    RF_URI_STRING,
)
from fal_small_images.row_result import RowResult


@pytest.fixture
def solr_client():
    """
    Creates a SolrClient instance for testing.
    """
    return SolrClient("https://mock-gateway-url.example.com")


def test_init(solr_client):
    """
    Test the initialization of SolrClient.
    """
    assert solr_client.gateway_url == "https://mock-gateway-url.example.com"
    assert solr_client.result is None


def test_obj_id_query_url(solr_client):
    """
    Test the generation of object ID query URL.
    """
    urns = ["urn-3:fhcl:164995", "DRS:urn-3:fhcl:124938"]
    expected_url = (
        "https://mock-gateway-url.example.com/api/"
        "get_object_ids?urns=urn-3:FHCL:164995&urns=urn-3:FHCL:124938&"
    )
    assert solr_client.obj_id_query_url(urns) == expected_url


def test_file_size_query_url(solr_client):
    """
    Test the generation of file size query URL.
    """
    obj_id = 12345
    expected_url = (
        "https://mock-gateway-url.example.com/api/get_image_list?id=12345"
    )
    assert solr_client.file_size_query_url(obj_id) == expected_url


def test_normalize_urns(solr_client):
    """
    Test the normalization of URNs.
    """
    urns = ["DRS:urn-3:fhcl:164995", "urn-3:FHCL:124938", "URN-3:fhcl:753159"]
    expected = ["urn-3:FHCL:164995", "urn-3:FHCL:124938", "urn-3:FHCL:753159"]
    assert solr_client.normalize_urns(urns) == expected


@patch("urllib.request.urlopen")
def test_get_object_ids(mock_urlopen, solr_client):
    """
    Test retrieving object IDs from URNs.
    """
    # Mock response data
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        {
            "response": {
                "docs": [{"object_id_num": 1001}, {"object_id_num": 1002}]
            }
        }
    ).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Call the method with test URNs
    urns = ["drs:urn-3:fhcl:164995", "urn-3:fhcl:124938"]
    result = solr_client.get_object_ids(urns)

    # Verify results
    assert result == {1001, 1002}

    # Verify the URL was correctly formed and passed to urlopen
    mock_urlopen.assert_called_once()
    call_args = mock_urlopen.call_args[0][0]

    expected_base = "https://mock-gateway-url.example.com/api/get_object_ids?"
    assert call_args.full_url.startswith(expected_base)
    assert call_args.full_url.endswith("&")
    assert call_args.full_url.count("urns=") == 2
    assert call_args.full_url.count("urns=urn-3:FHCL:164995") == 1
    assert call_args.full_url.count("urns=urn-3:FHCL:124938") == 1


@patch("urllib.request.urlopen")
def test_get_image_list(mock_urlopen, solr_client):
    """
    Test retrieving image list for an object ID.
    """
    # Mock response data
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps(
        {
            "response": {
                "docs": [
                    {
                        RF_FILE_ID: "file1",
                        RF_SIZE: 1024,
                        RF_ROLE: "DELIVERABLE",
                        RF_FILE_NAME: "image1.jpg",
                    },
                    {
                        RF_FILE_ID: "file2",
                        RF_SIZE: 2048,
                        RF_ROLE: "THUMBNAIL",
                        RF_FILE_NAME: "image2.jpg",
                    },
                ]
            }
        }
    ).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_response

    # Call the method with test object ID
    obj_id = 12345
    result = solr_client.get_image_list(obj_id)

    # Verify results
    assert len(result) == 2
    assert result[0][RF_FILE_ID] == "file1"
    assert result[1][RF_FILE_ID] == "file2"

    # Verify the URL was correctly formed and passed to urlopen
    actual_request = mock_urlopen.call_args[0][0]
    expected_base = "https://mock-gateway-url.example.com/api/get_image_list?"
    assert actual_request.full_url.startswith(expected_base)
    assert actual_request.full_url.endswith(f"id={obj_id}")


def test_is_deliverable_candidate(solr_client):
    """
    Test the is_deliverable_candidate method with various inputs.
    """
    # Valid deliverable
    image = {
        RF_ROLE: "DELIVERABLE",
        RF_ACCESS_FLAG: "P",
        RF_FILE_NAME: "image.jpg",
    }
    assert solr_client.is_deliverable_candidate(image) is True

    # Valid deliverable with restricted access
    image = {
        RF_ROLE: "DELIVERABLE",
        RF_ACCESS_FLAG: "R",
        RF_FILE_NAME: "image.jpg",
    }
    assert solr_client.is_deliverable_candidate(image) is True

    # Invalid role
    image = {
        RF_ROLE: "THUMBNAIL",
        RF_ACCESS_FLAG: "P",
        RF_FILE_NAME: "image.jpg",
    }
    assert solr_client.is_deliverable_candidate(image) is False

    # Invalid access flag
    image = {
        RF_ROLE: "DELIVERABLE",
        RF_ACCESS_FLAG: "N",
        RF_FILE_NAME: "image.jpg",
    }
    assert solr_client.is_deliverable_candidate(image) is False

    # JP2 file (should be rejected)
    image = {
        RF_ROLE: "DELIVERABLE",
        RF_ACCESS_FLAG: "P",
        RF_FILE_NAME: "image.JP2",
    }
    assert solr_client.is_deliverable_candidate(image) is False


def test_largest_deliverable_in_list(solr_client):
    """
    Test finding the largest deliverable image in a list.
    """
    # Setup client with a result object containing original URNs
    solr_client.result = RowResult(1, ["urn-3:FHCL:123"])

    # Test image list
    image_list = [
        {
            RF_URI_STRING: ["urn-3:FHCL:123"],  # Original thumbnail
            RF_SIZE: 100,
            RF_ROLE: "THUMBNAIL",
            RF_ACCESS_FLAG: "P",
            RF_FILE_NAME: "thumb.jpg",
        },
        {
            RF_URI_STRING: ["urn-3:FHCL:456"],
            RF_SIZE: 1000,
            RF_ROLE: "DELIVERABLE",
            RF_ACCESS_FLAG: "P",
            RF_FILE_NAME: "small.jpg",
        },
        {
            RF_URI_STRING: ["urn-3:FHCL:789"],
            RF_SIZE: 2000,
            RF_ROLE: "DELIVERABLE",
            RF_ACCESS_FLAG: "P",
            RF_FILE_NAME: "medium.jpg",
        },
        {
            RF_URI_STRING: ["urn-3:FHCL:101112"],
            RF_SIZE: 3000,
            RF_ROLE: "DELIVERABLE",
            RF_ACCESS_FLAG: "N",  # Not accessible
            RF_FILE_NAME: "large.jpg",
        },
        {
            RF_URI_STRING: ["urn-3:FHCL:131415"],
            RF_SIZE: 4000,
            RF_ROLE: "DELIVERABLE",
            RF_ACCESS_FLAG: "P",
            RF_FILE_NAME: "xlarge.jpg",
        },
    ]

    result = solr_client.largest_deliverable_in_list(image_list)

    # Verify the largest deliverable was selected
    assert result[RF_SIZE] == 4000
    assert result[RF_FILE_NAME] == "xlarge.jpg"

    # Verify the original thumbnail size was set correctly
    assert solr_client.result.original_thumbnail_size == 100


@patch.object(SolrClient, "get_object_ids")
@patch.object(SolrClient, "get_image_list")
@patch.object(SolrClient, "largest_deliverable_in_list")
def test_largest_deliverable_for_file(
    mock_largest_deliverable,
    mock_get_image_list,
    mock_get_object_ids,
    solr_client,
):
    """
    Test the end-to-end process of finding the largest deliverable file.
    """
    # Setup mocks
    mock_get_object_ids.return_value = {12345}
    mock_get_image_list.return_value = [{"file1": "data1"}, {"file2": "data2"}]
    mock_largest_deliverable.return_value = {
        "file_id": "best_file",
        "size": 5000,
    }

    # Call the method
    urns = ["drs:urn-3:fhcl:164995"]
    result = solr_client.largest_deliverable_for_file(urns)

    # Verify results
    assert result == {"file_id": "best_file", "size": 5000}

    # Verify all methods were called correctly
    mock_get_object_ids.assert_called_once_with(urns)
    mock_get_image_list.assert_called_once_with(12345)
    mock_largest_deliverable.assert_called_once_with(
        [{"file1": "data1"}, {"file2": "data2"}]
    )


@patch.object(SolrClient, "get_object_ids")
def test_largest_deliverable_for_file_no_object_id(
    mock_get_object_ids, solr_client
):
    """
    Test handling when no object IDs are found.
    """
    # Setup mocks to return empty set
    mock_get_object_ids.return_value = set()

    solr_client.result = RowResult(1, [])

    # Call the method
    urns = ["drs:urn-3:fhcl:164995"]
    result = solr_client.largest_deliverable_for_file(urns)

    # Verify results
    assert result is None
    assert solr_client.result.error == "Object id not found."


@patch.object(SolrClient, "get_object_ids")
def test_largest_deliverable_for_file_multiple_object_ids(
    mock_get_object_ids, solr_client
):
    """
    Test handling when multiple object IDs are found.
    """

    solr_client.result = RowResult(1, [])

    # Setup mocks to return multiple IDs
    mock_get_object_ids.return_value = {12345, 67890}

    # Call the method
    urns = ["drs:urn-3:fhcl:164995"]
    result = solr_client.largest_deliverable_for_file(urns)

    # Verify results
    assert result is None
    assert "Multiple object ids:" in solr_client.result.error


@patch.object(SolrClient, "largest_deliverable_for_file")
def test_process_row_success(mock_largest_deliverable, solr_client):
    """
    Test processing a row successfully.
    """
    # Setup mock
    mock_largest_deliverable.return_value = {
        RF_FILE_ID: "file1",
        RF_SIZE: 5000,
        RF_URI_STRING: ["urn-3:fhcl:789"],
        RF_FILE_NAME: "large.jpg",
    }

    # Call the method
    urns = ["drs:urn-3:fhcl:164995"]
    result = solr_client.process_row(1, urns)

    # Verify results
    assert result.found_deliverable_images is True
    assert result.row_number == 1
    assert result.original_urns == urns
    assert result.updated_large_size == 5000
    assert result.updated_large_urn == "urn-3:fhcl:789"


def test_process_row_no_filename(solr_client):
    """
    Test processing a row with no filename.
    """
    # Setup a RowResult that will return False for filename_present
    with patch(
        "fal_small_images.row_result.RowResult.filename_present", return_value=False
    ):
        # Call the method
        result = solr_client.process_row(1, [""])

        # Verify results
        assert result.skipped_because == "Row has no filename"
