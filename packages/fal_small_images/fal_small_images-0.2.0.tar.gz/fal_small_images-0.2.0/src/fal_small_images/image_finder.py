import csv

# import sys
# import os
from copy import copy

# from dotenv import load_dotenv
from .solr_client import SolrClient
from .row_result import RowResult


class ImageFinder:
    """
    Given a CSV file of object metadata exported from JSTOR, this
    searches Solr for larger versions of images listed in the
    input file.
    """

    def __init__(self, input_csv: str, output_csv: str, gateway_url: str):
        """
        Creates a new ImageFinder. input_csv is the path to the CSV
        containing exported JSTOR data. output_csv is the path to the
        output CSV file that will contain updated info.
        """
        self.input_csv = input_csv
        self.output_csv = output_csv
        self.gateway_url = gateway_url

    def run(self):
        """
        Reads each entry in the input CSV file, searches for larger images
        in Solr, and writes the output to the output CSV file. The output
        file will be identical to the input file, except that image URNs in
        the Filename column will be updated, when possible, to point to
        higher resolution images.
        """
        with open(self.output_csv, "w") as csv_out:
            writer = csv.writer(csv_out)
            row_number = 1
            with open(self.input_csv, "r") as csv_in:
                reader = csv.reader(csv_in)
                for row in reader:
                    output = copy(row)

                    # First row is headers, copy them to the output
                    # file, but don't process because there's no data.
                    if row_number == 1:
                        writer.writerow(output)
                        row_number += 1
                        print("Row 1: headers")
                        continue

                    # row[1] is Filename, which is a comma-separated string.
                    # Split the value into a list. Most will have two URNs,
                    # though some have only one.
                    urns = row[1].split(",")

                    # Ask Solr about these URNs
                    client = SolrClient(self.gateway_url)
                    row_result: RowResult = client.process_row(
                        row_number, urns
                    )

                    # If we found a larger image in Solr, update
                    # row[1] (Filename) in the output data with the
                    # URN of the larger image.
                    if row_result.found_larger_image():
                        old_urns = [u.replace("'", "") for u in urns]
                        new_urns = row_result.get_output_urns()
                        output[1] = new_urns

                    # Write the row of output data to the output CSV file.
                    writer.writerow(output)

                    # For now, since we're only running on the command line,
                    # let the user know what we did.
                    if row_result.found_larger_image():
                        print(
                            f"Row {row_number}: {",".join(old_urns)} "
                            f"-> {new_urns}"
                        )
                    else:
                        print(f"Row {row_number}: No changes")

                    row_number += 1
