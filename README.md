# mbtiles-s3-server [![CircleCI](https://circleci.com/gh/uktrade/mbtiles-s3-server.svg?style=shield)](https://circleci.com/gh/uktrade/mbtiles-s3-server) [![Test Coverage](https://api.codeclimate.com/v1/badges/c261eb01bc9446278cd3/test_coverage)](https://codeclimate.com/github/uktrade/mbtiles-s3-server/test_coverage)


Python server to on-the-fly extract and serve vector tiles from a single mbtiles file on S3. This avoids having to have an mbtiles file locally on the server, and means that the update of the tiles can be done by replacing a single object in S3.

Versioning must be enabled on the underlying S3 bucket.


## Installation

```bash
pip install mbtiles-s3-server
```

The libsqlite3 binary library is also required, but this is typically already installed on most systems. The earliest version of libsqlite3 known to work is 2012-12-12 (3.7.15).


## Usage

The server is configured using environment variables.

```bash
PORT=8080 \
AWS_S3_MBTILES_URL=https://my-bucket.s3.eu-west-2.amazonaws.com/tiles.mbtiles \
AWS_REGION=eu-west-2 \
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
    python -m mbtiles_s3_server
```
