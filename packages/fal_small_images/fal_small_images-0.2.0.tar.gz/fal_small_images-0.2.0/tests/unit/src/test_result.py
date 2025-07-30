from datetime import datetime, timezone
from unittest.mock import patch

from fal_small_images.result import Result


class TestResult:
    def test_init(self):
        """
        Test that Result is initialized with correct values.
        """
        result = Result("input.csv", "output.csv", True)

        assert result.input_file == "input.csv"
        assert result.output_file == "output.csv"
        assert result.is_dry_run is True
        assert isinstance(result.start_time, datetime)
        assert result.end_time is None
        assert result.records_processed == 0
        assert result.records_updated == {
            "one_urn": 0,
            "two_urns_no_orginal": 0,
            "two_urns_with_original": 0,
        }
        assert result.records_unchanged == 0
        assert result.processing_errors == {}

    @patch("fal_small_images.result.datetime")
    def test_init_with_start_time(self, mock_datetime):
        """
        Test that start_time is set from datetime.now().
        """
        mock_now = datetime(2023, 1, 1, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        result = Result("input.csv", "output.csv", False)

        assert result.start_time == mock_now
        mock_datetime.now.assert_called_once_with(timezone.utc)
