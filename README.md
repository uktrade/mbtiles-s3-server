# mbtiles-s3-server [![CircleCI](https://circleci.com/gh/uktrade/mbtiles-s3-server.svg?style=shield)](https://circleci.com/gh/uktrade/mbtiles-s3-server) [![Test Coverage](https://api.codeclimate.com/v1/badges/c261eb01bc9446278cd3/test_coverage)](https://codeclimate.com/github/uktrade/mbtiles-s3-server/test_coverage)


Python server to on-the-fly extract and serve vector tiles from mbtiles files on S3. Javascript, maps styles, fonts, and sprites are included so you can get setup quickly, especially with OpenMapTiles mbtiles files, but these are not required to be used. Versioning must be enabled on the underlying S3 bucket.

https://user-images.githubusercontent.com/13877/178137820-9734a903-6efb-4b1a-a7f0-44e59a290176.mov

Video showing expected performance. The server hosting the HTML is running locally, but mbtiles-s3-server is running on AWS, communicating with a real S3 bucket.


## Installation

```bash
pip install mbtiles-s3-server
```

The libsqlite3 binary library is also required, but this is typically already installed on most systems. The earliest version of libsqlite3 known to work is 2012-12-12 (3.7.15).


## Example usage

1. Create or obtain an mbtiles file, for example from https://openmaptiles.org/.

2. (Optional) Create another file with a page size of 65536 bytes (64KiB) using `VACUUM` or `VACUUM INTO`
  
   ```bash
   sqlite3 my-map.mbtiles "PRAGMA page_size=65536; VACUUM INTO 'mytiles-65536.mbtiles';"
   ```

   While this step is optional, performance with default mbtiles files that have smaller page sizes can be horrible to the point of being unusable - loading of a single tile can take many seconds. Performance of this server is limited by the latency of calls to S3, and this step effectively reduces the number of calls to S3 per map tile.

   Note both `VACUUM` and `VACUUM INTO` need disk space since they create another database which is approximately the size of the original file.

3. Upload this file to S3, for example to `https://my-bucket.s3.eu-west-2.amazonaws.com/mytiles-65536.mbtiles`

4. Ensure to have a IAM user that has `s3:GetObject` and `s3:GetObjectVersion` permissions on this S3 object, for example

   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "",
               "Effect": "Allow",
               "Action": [
                   "s3:GetObject",
                   "s3:GetObjectVersion"
               ],
               "Resource": [
                   "arn:aws:s3:::my-bucket/mytiles-65536.mbtiles"
               ]
           }
       ]
   }   
   ```

5. Start this server, configured with the location of this object and credentials for this user - it's configured using environment variables. You can assign the tiles file any version you like, in this case, `1.0.0`.

   ```bash
   PORT=8080 \
   MBTILES__1__URL=https://my-bucket.s3.eu-west-2.amazonaws.com/mytiles-65536.mbtiles \
   MBTILES__1__MIN_ZOOM=0 \
   MBTILES__1__MAX_ZOOM=14 \
   MBTILES__1__IDENTIFIER=mytiles \
   MBTILES__1__VERSION=1.0.0 \
   AWS_REGION=eu-west-2 \
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE \
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \
   HTTP_ACCESS_CONTROL_ALLOW_ORIGIN="*" \
       python -m mbtiles_s3_server
   ```

   The above is only to show what environment variables are needed - usually credentials should be avoided in shell commands. When developing locally, instead of specifying the `AWS_*` variables, consider using [aws-vault](https://github.com/99designs/aws-vault), which populates them for you.

   For example if you have a local AWS profile called `tiles`, you can run the below.

   ```bash
   PORT=8080 \
   MBTILES__1__URL=https://my-bucket.s3.eu-west-2.amazonaws.com/mytiles-65536.mbtiles \
   MBTILES__1__MIN_ZOOM=0 \
   MBTILES__1__MAX_ZOOM=14 \
   MBTILES__1__IDENTIFIER=mytiles \
   MBTILES__1__VERSION=1.0.0 \
   HTTP_ACCESS_CONTROL_ALLOW_ORIGIN="*" \
       aws-vault exec tiles -- python -m mbtiles_s3_server
   ```

6. On your user-facing site, include HTML that loads these tiles from this server, for example to load maps from a server started as above running locally serving OpenMapTiles

   ```html
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <title>Example map</title>
        <meta name="viewport" content="initial-scale=1,maximum-scale=1,user-scalable=no">
        <script src="http://localhost:8080/v1/static/maplibre-gl@2.1.9/maplibre-gl.js"></script>
        <link href="http://localhost:8080/v1/static/maplibre-gl@2.1.9/maplibre-gl.css" rel="stylesheet">
        <style>
          body, html, #map {margin: 0; padding: 0; height: 100%; width: 100%}
        </style>
      </head>
      <body>
        <div id="map"></div>
        <script>
        var map = new maplibregl.Map({
            container: 'map',
            style: 'http://localhost:8080/v1/styles/osm-bright-gl-style@1.0.0/style.json?fonts=fonts-gl@1.0.0&tiles=mytiles@1.0.0',
            center: [0, 0],
            zoom: 1,
            attributionControl: false
        });
        map.addControl(new maplibregl.AttributionControl({
            customAttribution: '<a href="https://openmaptiles.org/">© OpenMapTiles</a> <a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>'
        }), 'bottom-right');
        </script>
      </body>
    </html>
   ```

   This HTML is included in this repository in [example.html](./example.html). A simple server can be started to view it by

   ```bash
   python -m http.server 8081 --bind 127.0.0.1
   ````

   and going to [http://localhost:8081/example.html](http://localhost:8081/example.html)


## For the curious, advanced, or developers of this server itself

Hosting your own vector map tiles to show them in a browser requires quite a few components:

1. **JavaScript and CSS**

   A Javascript and CSS library, such as [MapLibre GL](https://github.com/maplibre/maplibre-gl-js), and your own code to run this library, pointing it to a style file

2. **Style file**

   A JSON file that defines how the library should visually style the map data, and where it should find the map tiles, glyphs (fonts), and the sprite. This server transforms the built-in Style files on the fly to be able to refer to any map data.

3. **Glyphs** (fonts)

   Different fonts can be used for different labels and zoom levels, as defined in the Style file. The fonts must Signed Distance Field (SDF) fonts wrapped in a particular Protocol Buffer format. The Style file can refer to "stacks" of fonts; but unlike CSS, the server combines the fonts on the fly in an API where the resulting "font" has at most one glyph from each source font.

4. **Sprite**

   A sprite is actually 4 URLs: a JSON index file and a single PNG file, and a "@2x" JSON index file and PNG files for higher pixel ratio devices (e.g. Retina). The JSON files contains the offsets and sizes of images within corresponding PNG file. The style file refers the common "base" of these. For example, if the style file has `"sprite":"https://my.test/sprite"` then the 4 files must be at `https://my.test/sprite.json`, `https://my.test/sprite.png`, `https://my.test/sprite@2x.json` and `https://my.test/sprite@2x.png`.

5. **Vector map tiles**

   A set of often millions of tiles each covering a different location and different zoom level. These can be distributed as a single mbtiles file, but this is not the format that the Javascript library accepts. This on-the-fly conversion from the mbtiles file to tiles is the main feature of this server.

   The mbtiles file is a SQLite file, containing gzipped Mapbox Vector Tile tiles. This server leaves the un-gzipping to the browser, by sending tiles with a `content-encoding: gzip` header, which results in browser un-gzipping the tile data before it hits the Javascript.


## Licenses

The code of the server itself is released under the MIT license. However, several components included in [mbtiles_s3_server/vendor/](./mbtiles_s3_server/vendor/) are released under different licenses.
