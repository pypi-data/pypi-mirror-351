# FAL Small Images

This project attempts to find and fix low resolution images from the Fine Arts Library that found their way into JSTOR Forum.

Given a CSV file exported from JSTOR Forum, ImageFinder searches the Solr database at libsearch8elb-prod.lib.harvard.edu for higher resolution copies of the same images. If it finds them, it replaces the low resolution image URNs in the Filename column of the output CSV file. The input and output CSV files will have identical structures, and no data outside the Filename column will be changed in the output.

## Status

You'll find a sample input file in the test/files directory which you can run with this command:

```
python main.py ./tests/files/images.csv output.csv
```

## Requirements

  - Python 3+ (built with Python 3.13)
  - Access to the fal-small-images-gateway API server (which proxies requests to Solr)

Now run `uv sync` and you should be ready to go.

See .env.example for info about required env vars.
