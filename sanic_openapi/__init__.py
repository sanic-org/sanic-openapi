import os
from enum import Enum

from sanic.blueprints import Blueprint
from sanic.response import json

from .doc import route_specs, RouteSpec, serialize_schema
from . import config

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(dir_path + '/../swagger-ui')

openapi_blueprint = Blueprint('openapi', url_prefix='openapi')
swagger_blueprint = Blueprint('swagger', url_prefix='swagger')

swagger_blueprint.static('/', dir_path)

_swagger = {}

@openapi_blueprint.listener('before_server_start')
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

    paths = {}
    for uri, route in app.router.routes_all.items():
        if uri.startswith("/swagger") or uri.startswith("/openapi") \
                or '<file_uri' in uri: #TODO: add static flag in sanic routes
            continue

        route_spec = route_specs.get(route.handler) or RouteSpec()
        consumes_content_types = route_spec.consumes_content_type or config.CONSUMES_CONTENT_TYPE
        produces_content_types = route_spec.produces_content_type or config.PRODUCES_CONTENT_TYPE

        # --------------------------------------------------------------- #
        # Methods
        # --------------------------------------------------------------- #

        methods = {}
        for _method in (route.methods or ['GET']):
            method = {
                "operationId": route_spec.operation or route.handler.__name__,
                "parameters": []
            }
            if route_spec.summary:
                method['summary'] = route_spec.summary
            if route_spec.description:
                method['description'] = route_spec.description
            if method not in ('GET', 'DELETE'):
                method['consumes'] = consumes_content_types
                if route_spec.consumes:
                    parameter = serialize_schema(route_spec.consumes)
                    parameter['in'] = 'body'
                    parameter['name'] = 'body'
                    method['parameters'].append(parameter)

            method['produces'] = produces_content_types
            methods[_method.lower()] = method

        paths[uri] = methods

    _swagger['paths'] = paths


@openapi_blueprint.route('/swagger.json')
def swagger(request):
    return json(_swagger)


