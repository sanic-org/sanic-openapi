import os

from sanic.blueprints import Blueprint
from sanic.response import json

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(dir_path + '/../swagger-ui')

blueprint = Blueprint('openapi')

blueprint.static('/swagger', dir_path)

_swagger = {}


@blueprint.listener('before_server_start')
def build_swagger(app, loop):
    _swagger['swagger'] = '2.0'
    _swagger['info'] = {
        "version": "1.0.0",
        "title": "Sanic Swagger",
        "description": "Thing and stuff",
        # "termsOfService": "",
        # "contact": {
        #     "email": ""
        # },
        # "license": {
        #     "name": "",
        #     "url": ""
        # }
    }

    paths = []
    for uri, route in app.router.routes_all.items():
        if uri.startswith("/swagger") or uri.startswith("/openapi") \
                or '<file_uri' in uri:
            continue
        print(uri)
        print(route)


@blueprint.route('/openapi/swagger.json')
def swagger(request):
    return json(_swagger)
