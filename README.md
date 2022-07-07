# mbtiles-s3-server [![CircleCI](https://circleci.com/gh/uktrade/mbtiles-s3-server.svg?style=shield)](https://circleci.com/gh/uktrade/mbtiles-s3-server) [![Test Coverage](https://api.codeclimate.com/v1/badges/c261eb01bc9446278cd3/test_coverage)](https://codeclimate.com/github/uktrade/mbtiles-s3-server/test_coverage)


Python server to on-the-fly extract and serve vector tiles from mbtiles files on S3. This avoids having to have potentially very large mbtiles file locally on the web server. Javascript, maps styles, fonts, and sprites are included so you can get setup quickly, but are not required to be used.

Versioning must be enabled on the underlying S3 bucket

> Work in progress. Not all features below are implemented. This document serves as a rough design spec.


## Installation

```bash
pip install mbtiles-s3-server
```

The libsqlite3 binary library is also required, but this is typically already installed on most systems. The earliest version of libsqlite3 known to work is 2012-12-12 (3.7.15).


## Usage

The server is configured using environment variables.

```bash
PORT=8080 \
MBTILES__1__URL=https://my-bucket.s3.eu-west-2.amazonaws.com/tiles.mbtiles \
MBTILES__1__IDENTIFIER=mytiles \
AWS_REGION=eu-west-2 \
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
AWS_SESSION_TOKEN="Only needed for temporary credentials" \
    python -m mbtiles_s3_server
```


## For the curious, advanced, or developers of this server itself

Hosting your own vector map tiles to show them in a browser requires quite a few components:

1. **JavaScript**

   A library such as [MapLibre GL](https://github.com/maplibre/maplibre-gl-js), and your own code to run the library, and point it to a style file

2. **Style file**

   A JSON file that defines how the library should style the map tiles, and where it should find the map tiles, glyphs (fonts), and the sprite

3. **Glyphs** (fonts)

   Sets of fonts; different fonts can be used for different labels and zoom levels, as defined in the Style file

4. **Sprite**

   A single JSON index file and a single PNG file; the JSON file contains the offsets and sizes of images within the single PNG file

5. **Vector map tiles**

   A set of often hundreds of thousands of tiles each covering a different location and different zoom level. These can be distributed as a single mbtiles file, but this is not the format that the Javascript library accepts. This on-the-fly conversion from the mbtiles file to tiles is the main feature of this server.


## Licenses

The code of the server itself is released under the MIT license. However, several components included are released under separate licenses.
