# mbtiles-s3-server [![CircleCI](https://circleci.com/gh/uktrade/mbtiles-s3-server.svg?style=shield)](https://circleci.com/gh/uktrade/mbtiles-s3-server) [![Test Coverage](https://api.codeclimate.com/v1/badges/c261eb01bc9446278cd3/test_coverage)](https://codeclimate.com/github/uktrade/mbtiles-s3-server/test_coverage)


Python server to on-the-fly extract and serve vector tiles from a single mbtiles file on S3. This avoids having to have an mbtiles file locally on the server, and means that the update of the tiles can be done by replacing a single object in S3.

Versioning must be enabled on the underlying S3 bucket

> Work in progress. Not all features below are implemented. This document serves as a rough design spec.


## Why does this exist?

Hosting your own vector map tiles and then showing them in a browser has quite a few moving parts, and this project attempts to make it as straightforward as possible - for example by providing reasonable defaults which can then be overridden. A core feature of this server is that S3 is leveraged wherever possible, which allows for updates without a re-deployment.

The components are:

1. **JavaScript**

   A library such as [MapLibre GL](https://github.com/maplibre/maplibre-gl-js), and your own code to run the library, and point it to a style file

2. **Style file**

   A JSON file that tells the library how to find the map tiles, how to style them, how to find to glyphs (fonts), and how to find the sprite

3. **Glyphs** (fonts)

   Sets of fonts; the style file specified which font is used for what sort of label or zoom levels

4. **Sprite**

   A single JSON index file with URLs to and offsets in image files; the style file determines when these are used

5. **Vector map tiles**

   A set of often hundreds of thousands of tiles each covering a different location and different zoom level. These can be distributed as a single mbtiles file, but this is not the format that the Javascript library accepts. This on-the-fly conversion from the mbtiles file to tiles is the main feature of this server.


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
AWS_SESSION_TOKEN="Only needed for temporary credentials" \
    python -m mbtiles_s3_server
```

## Licenses

The code of the server itself is released under the MIT license. However, several components included are released under separate licenses.
