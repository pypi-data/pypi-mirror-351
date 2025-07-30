from datetime import datetime, timezone


class Result:
    """
    Result contains a summary of transformations done between the
    input and output CSV files. Not used yet, but coming soon.
    """

    def __init__(self, input_file: str, output_file: str, is_dry_run: bool):
        self.input_file: str = input_file
        self.output_file: str = output_file
        self.is_dry_run: bool = is_dry_run
        self.start_time: datetime = datetime.now(timezone.utc)
        self.end_time: datetime = None

        self.records_processed: int = 0
        self.records_updated: dict[str, int] = {
            "one_urn": 0,
            "two_urns_no_orginal": 0,
            "two_urns_with_original": 0,
        }
        self.records_unchanged: int = 0
        self.processing_errors: dict[str, str] = {}
