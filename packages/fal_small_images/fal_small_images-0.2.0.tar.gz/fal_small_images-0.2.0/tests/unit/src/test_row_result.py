from unittest.mock import MagicMock

from fal_small_images.row_result import RowResult


class TestRowResult:
    def test_init(self):
        """
        Test that RowResult is initialized with correct values.
        """
        row_result = RowResult(
            42, ["urn-3:fhcl:165719", "drs:urn-3:fhcl:126392"]
        )

        assert row_result.row_number == 42
        assert row_result.original_urns == [
            "urn-3:fhcl:165719",
            "drs:urn-3:fhcl:126392",
        ]
        assert row_result.original_urn_count == 2
        assert row_result.original_large_urn == ""
        assert row_result.original_large_size == 0
        assert row_result.original_thumbnail_urn == ""
        assert row_result.original_thumbnail_size == 0
        assert row_result.updated_large_urn == ""
        assert row_result.updated_large_size == 0
        assert row_result.updated_thumbnail_urn == ""
        assert row_result.updated_thumbnail_size == 0
        assert row_result.skipped_because is None
        assert row_result.found_deliverable_images is False
        assert row_result.error is None

    def test_filename_present_true(self):
        """
        Test filename_present returns True when original_urns is not empty.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])

        assert row_result.filename_present() is True
        assert row_result.skipped_because is None

    def test_filename_present_false(self):
        """
        Test filename_present returns False when original_urns is empty.
        """
        row_result = RowResult(1, [])

        assert row_result.filename_present() is False
        assert row_result.skipped_because == "Record has no filename"

    def test_skipped_true(self):
        """
        Test skipped returns True when skipped_because is not None.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.skipped_because = "Some reason"

        assert row_result.skipped() is True

    def test_skipped_false(self):
        """
        Test skipped returns False when skipped_because is None.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])

        assert row_result.skipped() is False

    def test_set_largest_image_one_urn(self):
        """
        Test set_largest_image with one original URN.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        image = {
            "file_huldrsadmin_uri_string": ["urn-3:fhcl:999999"],
            "file_premis_size_num": 12345,
        }

        row_result.set_largest_image(image)

        assert row_result.updated_large_urn == "urn-3:fhcl:999999"
        assert row_result.updated_large_size == 12345

    def test_set_largest_image_two_urns_different(self):
        """
        Test set_largest_image with two original URNs and different new URN.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719", "urn-3:fhcl:126392"])
        image = {
            "file_huldrsadmin_uri_string": ["urn-3:fhcl:999999"],
            "file_premis_size_num": 12345,
        }

        row_result.set_largest_image(image)

        assert row_result.updated_large_urn == "urn-3:fhcl:999999"
        assert row_result.updated_large_size == 12345

    def test_set_largest_image_two_urns_same(self):
        """
        Test set_largest_image with two original URNs and same new URN.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719", "urn-3:fhcl:126392"])
        image = {
            "file_huldrsadmin_uri_string": ["urn-3:fhcl:126392"],
            "file_premis_size_num": 12345,
        }

        row_result.set_largest_image(image)

        # Note: The function has no return value and doesn't update
        # when the largest urn matches the second original urn
        assert row_result.updated_large_urn == ""
        assert row_result.updated_large_size == 0

    def test_found_larger_image_true(self):
        """
        Test found_larger_image returns True when a new URN is found.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.updated_large_urn = "urn-3:fhcl:999999"

        assert row_result.found_larger_image() is True

    def test_found_larger_image_false_exact_match(self):
        """
        Test found_larger_image returns False when URN exactly matches
        original.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.updated_large_urn = "urn-3:fhcl:165719"

        assert row_result.found_larger_image() is False

    def test_found_larger_image_false_case_insensitive(self):
        """
        Test found_larger_image returns False when URN matches original
        case-insensitively.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.updated_large_urn = "URN-3:FHCL:165719"

        assert row_result.found_larger_image() is False

    def test_found_larger_image_false_with_drs_prefix(self):
        """
        Test found_larger_image returns False when URN matches original
        with drs prefix.
        """
        row_result = RowResult(1, ["drs:urn-3:fhcl:165719"])
        row_result.updated_large_urn = "urn-3:fhcl:165719"

        assert row_result.found_larger_image() is False

    def test_get_output_urns_empty(self):
        """
        Test get_output_urns returns empty string when no original URNs.
        """
        row_result = RowResult(1, [])

        assert row_result.get_output_urns() == ""

    def test_get_output_urns_no_new_image_one_urn(self):
        """
        Test get_output_urns returns original URN when no larger image found.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.updated_large_urn = "urn-3:fhcl:165722"

        assert row_result.get_output_urns() == "urn-3:fhcl:165722"

    def test_get_output_urns_no_new_image_two_urns(self):
        """
        Test get_output_urns returns original URNs when no larger image found.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719", "urn-3:fhcl:126392"])
        row_result.updated_large_urn = "urn-3:fhcl:165755"
        output = row_result.get_output_urns()
        assert output == "urn-3:fhcl:165719,urn-3:fhcl:165755"

    def test_get_output_urns_with_new_image_one_urn(self):
        """
        Test get_output_urns returns new URN when larger image found
        with one original.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719"])
        row_result.updated_large_urn = "URN-3:FHCL:999999"

        # Mock found_larger_image to return True
        row_result.found_larger_image = MagicMock(return_value=True)

        assert row_result.get_output_urns() == "urn-3:fhcl:999999"
        row_result.found_larger_image.assert_called_once()

    def test_get_output_urns_with_new_image_two_urns(self):
        """
        Test get_output_urns returns combination with new URN when larger
        image found with two originals.
        """
        row_result = RowResult(1, ["urn-3:fhcl:165719", "urn-3:fhcl:126392"])
        row_result.updated_large_urn = "URN-3:FHCL:999999"

        # Mock found_larger_image to return True
        row_result.found_larger_image = MagicMock(return_value=True)

        output = row_result.get_output_urns()
        assert output == "urn-3:fhcl:165719,urn-3:fhcl:999999"

        row_result.found_larger_image.assert_called_once()
