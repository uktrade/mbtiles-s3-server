from gevent import (
    monkey,
)
monkey.patch_all()

import logging
import os
import signal
import sys

import gevent
from gevent.pywsgi import (
    WSGIServer,
)
from flask import (
    Flask,
    Response,
)
import httpx
from sqlite_s3_query import sqlite_s3_query


def mbtiles_s3_server(
        logger,
        port,
        mbtiles_url,
):
    server = None
    http_client = httpx.Client()

    def start():
        server.serve_forever()

    def stop():
        server.stop()

    app = Flask('app')

    sql = '''
        SELECT
            tile_data
        FROM
            tiles
        WHERE
            tile_column=? AND
            tile_row=? AND
            zoom_level=?
        LIMIT 1
    '''

    def get_tile(x, y, z):
        tile_data = None
        with \
                sqlite_s3_query(url=mbtiles_url, get_http_client=lambda: http_client) as query, \
                query(sql, params=(x, y, z)) as (columns, rows):

            for row in rows:
                tile_data = row[0]

        return \
            Response(status=200, response=tile_data) if tile_data is not None else \
            Response(status=404)

    app.add_url_rule('/<int:x>/<int:y>/<int:z>', view_func=get_tile)
    server = WSGIServer(('0.0.0.0', port), app, log=app.logger)

    return start, stop


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    start, stop = mbtiles_s3_server(
        logger,
        int(os.environ['PORT']),
        os.environ['AWS_S3_MBTILES_URL'],
    )

    gevent.signal_handler(signal.SIGTERM, stop)
    start()
    gevent.get_hub().join()
    logger.info('Shut down gracefully')


if __name__ == '__main__':
    main()
