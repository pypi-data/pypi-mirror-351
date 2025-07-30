import os
import sys
from dotenv import load_dotenv

from .image_finder import ImageFinder


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("Usage: image_finder.py <input.csv> <output.csv>")
        sys.exit(1)

    load_dotenv()
    gateway_url = os.getenv("FAL_SMALL_IMAGES_GATEWAY_URL")
    if not gateway_url:
        print(
            "Set environment var FAL_SMALL_IMAGES_GATEWAY_URL "
            "to point to the fal-small-images-gateway."
        )
        sys.exit(1)

    image_finder = ImageFinder(
        input_csv=sys.argv[1],
        output_csv=sys.argv[2],
        gateway_url=gateway_url,
    )
    image_finder.run()
