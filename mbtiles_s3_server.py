from gevent import (
    monkey,
)
monkey.patch_all()

import itertools
import json
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
    request,
)
import httpx
from sqlite_s3_query import sqlite_s3_query


def mbtiles_s3_server(
        logger,
        port,
        mbtiles,
        http_access_control_allow_origin,
):
    server = None
    http_client = httpx.Client()

    def read(path):
        real_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), path)
        with open(real_path, 'rb') as f:
            return f.read()

    mbtiles_dict = {
        mbtile['IDENTIFIER']: mbtile
        for mbtile in mbtiles
    }

    styles_dict = {
        ('positron-gl-style', '1.8', 'style.json'):
        read('mbtiles_s3_server/vendor/positron-gl-style@1.8/style.json'),
    }
    statics_dict = {
        ('maplibre-gl', '2.1.9', 'maplibre-gl.css'): {
            'bytes': read('mbtiles_s3_server/vendor/maplibre-gl@2.1.9/maplibre-gl.css'),
            'mime': 'text/css',
        },
        ('maplibre-gl', '2.1.9', 'maplibre-gl.js'): {
            'bytes': read('mbtiles_s3_server/vendor/maplibre-gl@2.1.9/maplibre-gl.js'),
            'mime': 'application/javascript',
        },
    }

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
            zoom_level=? AND
            tile_column=? AND
            tile_row=?
        LIMIT 1
    '''

    def get_tile(identifier, z, x, y):
        try:
            mbtiles_url = mbtiles_dict[identifier]['URL']
        except KeyError:
            return Response(status=404)

        tile_data = None
        with \
                sqlite_s3_query(url=mbtiles_url, get_http_client=lambda: http_client) as query, \
                query(sql, params=(z, x, y)) as (columns, rows):

            for row in rows:
                tile_data = row[0]

        return \
            Response(status=200, response=tile_data) if tile_data is not None else \
            Response(status=404)

    def get_styles(identifier, version, file):
        try:
            style_bytes = styles_dict[(identifier, version, file)]
        except KeyError:
            return Response(status=404)

        try:
            tiles_identifier = request.args['tiles']
        except KeyError:
            return Response(status=400)

        style_dict = json.loads(style_bytes)
        style_dict['sources']['openmaptiles'] = {
            'type': 'vector',
            'tiles': [
                request.url_root + 'tiles/' + tiles_identifier + '/{z}/{x}/{y}'
            ],
        }

        return Response(status=200, content_type='application/json',
                        response=json.dumps(style_dict))

    def get_static(identifier, version, file):
        try:
            static_dict = statics_dict[(identifier, version, file)]
        except KeyError:
            return Response(status=404)

        return Response(status=200, content_type=static_dict['mime'],
                        response=static_dict['bytes'])

    @app.after_request
    def _add_headers(resp):
        if http_access_control_allow_origin:
            resp.headers['access-control-allow-origin'] = http_access_control_allow_origin
        return resp

    app.add_url_rule('/v1/tiles/<string:identifier>/<int:z>/<int:x>/<int:y>', view_func=get_tile)
    app.add_url_rule(
        '/v1/styles/<string:identifier>@<string:version>/<string:file>', view_func=get_styles)
    app.add_url_rule(
        '/v1/static/<string:identifier>@<string:version>/<string:file>', view_func=get_static)
    server = WSGIServer(('0.0.0.0', port), app, log=app.logger)

    return start, stop


def normalise_environment(key_values):
    # Separator is chosen to
    # - show the structure of variables fairly easily;
    # - avoid problems, since underscores are usual in environment variables
    separator = '__'

    def get_first_component(key):
        return key.split(separator)[0]

    def get_later_components(key):
        return separator.join(key.split(separator)[1:])

    without_more_components = {
        key: value
        for key, value in key_values.items()
        if not get_later_components(key)
    }

    with_more_components = {
        key: value
        for key, value in key_values.items()
        if get_later_components(key)
    }

    def grouped_by_first_component(items):
        def by_first_component(item):
            return get_first_component(item[0])

        # groupby requires the items to be sorted by the grouping key
        return itertools.groupby(
            sorted(items, key=by_first_component),
            by_first_component,
        )

    def items_with_first_component(items, first_component):
        return {
            get_later_components(key): value
            for key, value in items
            if get_first_component(key) == first_component
        }

    nested_structured_dict = {
        **without_more_components, **{
            first_component: normalise_environment(
                items_with_first_component(items, first_component))
            for first_component, items in grouped_by_first_component(with_more_components.items())
        }}

    def all_keys_are_ints():
        def is_int(string):
            try:
                int(string)
                return True
            except ValueError:
                return False

        return all([is_int(key) for key, value in nested_structured_dict.items()])

    def list_sorted_by_int_key():
        return [
            value
            for key, value in sorted(
                nested_structured_dict.items(),
                key=lambda key_value: int(key_value[0])
            )
        ]

    return \
        list_sorted_by_int_key() if all_keys_are_ints() else \
        nested_structured_dict


def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)

    env = normalise_environment(os.environ)

    start, stop = mbtiles_s3_server(
        logger,
        int(os.environ['PORT']),
        env['MBTILES'],
        env.get('HTTP_ACCESS_CONTROL_ALLOW_ORIGIN'),
    )

    gevent.signal_handler(signal.SIGTERM, stop)
    start()
    gevent.get_hub().join()
    logger.info('Shut down gracefully')


if __name__ == '__main__':
    main()
