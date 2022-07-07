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
from sqlite_s3_query import sqlite_s3_query


def mbtiles_s3_server(
        logger,
        port,
        mbtiles_url,
):
    server = None

    def start():
        server.serve_forever()

    def stop():
        server.stop()

    app = Flask('app')

    def get_tile():
        with sqlite_s3_query(url=mbtiles_url) as query:
            with query('SELECT * FROM sqlite_master', params=()) as (columns, rows):
                pass
                for row in rows:
                    pass

        return Response()

    app.add_url_rule('/', view_func=get_tile)
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
