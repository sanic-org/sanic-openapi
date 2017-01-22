import os
import re
from itertools import repeat

from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import CompositionView

from .doc import route_specs, RouteSpec, serialize_schema, definitions
from . import config

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(dir_path + '/swagger-ui')

openapi_blueprint = Blueprint('openapi', url_prefix='openapi')
swagger_blueprint = Blueprint('swagger', url_prefix='swagger')

swagger_blueprint.static('/', dir_path + '/index.html')
swagger_blueprint.static('/', dir_path)

_spec = {}


# Removes all null values from a dictionary
def remove_nulls(dictionary, deep=True):
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


@openapi_blueprint.listener('before_server_start')
def build_spec(app, loop):
    _spec['swagger'] = '2.0'
    _spec['info'] = {
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
    _spec['schemes'] = [
        'http'
    ]

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

        # Build list of methods and their handler functions
        handler_type = type(route.handler)
        if handler_type is CompositionView:
            view = route.handler
            method_handlers = view.handlers.items()
        else:
            method_handlers = zip(route.methods, repeat(route.handler))

        methods = {}
        for _method, _handler in method_handlers:
            endpoint = remove_nulls({
                'operationId': route_spec.operation or _handler.__name__,
                'summary': route_spec.summary,
                'description': route_spec.description,
                'consumes': consumes_content_types,
                'produces': produces_content_types,
                'parameters': [{
                    **serialize_schema(parameter.cast),
                    'required': True,
                    'in': 'path',
                    'name': parameter.name,
                } for parameter in route.parameters],
                'responses': {
                    "200": {
                        "description": None,
                        "examples": None,
                        "schema": serialize_schema(route_spec.produces) if route_spec.produces else None
                    }
                },
            })
            if _method not in ('GET', 'DELETE'):
                if route_spec.consumes:
                    endpoint['parameters'].append({
                        **serialize_schema(route_spec.consumes),
                        'in': 'body',
                        'name': 'body',
                    })

            methods[_method.lower()] = endpoint

        uri_parsed = uri
        for parameter in route.parameters:
            uri_parsed = re.sub('<'+parameter.name+'.+?>', '{'+parameter.name+'}', uri_parsed)

        paths[uri_parsed] = methods

    # --------------------------------------------------------------- #
    # Definitions
    # --------------------------------------------------------------- #
    _spec['definitions'] = { obj.object_name: definition for cls, (obj, definition) in definitions.items()}

    _spec['paths'] = paths


@openapi_blueprint.route('/spec.json')
def spec(request):
    return json(_spec)


