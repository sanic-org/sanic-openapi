import re
from itertools import repeat

from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import CompositionView

from .doc import excluded_paths, definitions, route_specs, serialize_schema
from .doc import RouteSpec


blueprint = Blueprint('openapi', url_prefix='openapi')

_spec = {}


# Removes all null values from a dictionary
def remove_nulls(dictionary, deep=True):
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


@blueprint.listener('before_server_start')
def build_spec(app, loop):
    _spec['swagger'] = '2.0'
    _spec['info'] = {
        "version": getattr(app.config, 'API_VERSION', '1.0.0'),
        "title": getattr(app.config, 'API_TITLE', 'API'),
        "description": getattr(app.config, 'API_DESCRIPTION', ''),
        "termsOfService": getattr(app.config, 'API_TERMS_OF_SERVICE', ''),
        "contact": {
            "email": getattr(app.config, 'API_CONTACT_EMAIL', None),
        },
        "license": {
            "name": getattr(app.config, 'API_LICENSE_NAME', None),
            "url": getattr(app.config, 'API_LICENSE_URL', None),
        }
    }
    _spec['schemes'] = getattr(app.config, 'API_SCHEMES', ['http'])

    # --------------------------------------------------------------- #
    # Blueprint Tags
    # --------------------------------------------------------------- #

    for blueprint in app.blueprints.values():
        if hasattr(blueprint, 'routes'):
            for route in blueprint.routes:
                route_spec = route_specs[route.handler]
                route_spec.blueprint = blueprint
                if not route_spec.tags:
                    route_spec.tags.append(blueprint.name)

    paths = {}
    for uri, route in app.router.routes_all.items():
        if uri.startswith("/swagger") or uri.startswith("/openapi") \
                or '<file_uri' in uri:
                # TODO: add static flag in sanic routes
            continue
        if any(uri.startswith(path) for path in excluded_paths):
            continue

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
            _methods = {
                'GET': lambda: _handler.view_class.get,
                'POST': lambda: _handler.view_class.post,
                'PUT': lambda: _handler.view_class.put,
                'PATCH': lambda: _handler.view_class.patch,
                'DELETE': lambda: _handler.view_class.delete,
            }
            if 'view_class' in dir(_handler):
                route_spec = route_specs.get(_methods.get(_method)()) or RouteSpec()
            else:
                route_spec = route_specs.get(_handler) or RouteSpec()

            if _method == 'OPTIONS' or route_spec.exclude:
                continue

            consumes_content_types = route_spec.consumes_content_type or \
                getattr(app.config, 'API_CONSUMES_CONTENT_TYPES', ['application/json'])
            produces_content_types = route_spec.produces_content_type or \
                getattr(app.config, 'API_PRODUCES_CONTENT_TYPES', ['application/json'])

            # Parameters - Path & Query String
            route_parameters = []
            for parameter in route.parameters:
                param_description = route_spec.path_parameters[parameter.name] \
                    if parameter.name in route_spec.path_parameters.keys() else ''
                route_parameters.append({
                    **serialize_schema(parameter.cast),
                    'required': True,
                    'in': 'path',
                    'name': parameter.name,
                    'description': param_description,
                })

            for consumer in route_spec.consumes:
                spec = serialize_schema(consumer.field)
                if 'properties' in spec:
                    for name, prop_spec in spec['properties'].items():
                        route_param = {
                            **prop_spec,
                            'required': consumer.required,
                            'in': consumer.location,
                            'name': name,
                            'description': consumer.description,
                        }
                else:
                    route_param = {
                        **spec,
                        'required': consumer.required,
                        'in': consumer.location,
                        'name': consumer.field.name if hasattr(consumer.field, 'name') else 'body',
                        'description': consumer.description,
                    }

                if '$ref' in route_param:
                    route_param["schema"] = {'$ref': route_param['$ref']}
                    del route_param['$ref']

                route_parameters.append(route_param)

            responses = {
                '200': {
                    'schema': serialize_schema(route_spec.produces.field) if route_spec.produces else None,
                    'description': route_spec.produces.description if route_spec.produces else None,
                }
            }

            for (status_code, route_field) in route_spec.responses:
                if route_field.override_default:
                    del responses['200']

                responses[str(status_code)] = {
                    'schema': serialize_schema(route_field.field),
                    'description': route_field.description,
                }

            endpoint = remove_nulls({
                'operationId': route_spec.operation or route.name,
                'summary': route_spec.summary,
                'description': route_spec.description,
                'consumes': consumes_content_types,
                'produces': produces_content_types,
                'tags': route_spec.tags or None,
                'parameters': route_parameters,
                'responses': responses,
            })

            methods[_method.lower()] = endpoint

        uri_parsed = uri
        for parameter in route.parameters:
            uri_parsed = re.sub('<'+parameter.name+'.*?>', '{'+parameter.name+'}', uri_parsed)

        paths[uri_parsed] = methods

    # --------------------------------------------------------------- #
    # Definitions
    # --------------------------------------------------------------- #

    _spec['definitions'] = {obj.object_name: definition for cls, (obj, definition) in definitions.items()}

    # --------------------------------------------------------------- #
    # Tags
    # --------------------------------------------------------------- #

    # TODO: figure out how to get descriptions in these
    tags = {}
    for route_spec in route_specs.values():
        if route_spec.blueprint and route_spec.blueprint.name in ('swagger', 'openapi'):
                # TODO: add static flag in sanic routes
            continue
        for tag in route_spec.tags:
            tags[tag] = True
    _spec['tags'] = [{"name": name} for name in tags.keys()]

    _spec['paths'] = paths


@blueprint.route('/spec.json')
def spec(_):
    return json(_spec)
