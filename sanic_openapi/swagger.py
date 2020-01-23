import os
import re
from itertools import repeat
from typing import Dict

from sanic import Sanic, response
from sanic.views import CompositionView

from .doc import RouteSpecs, serialize_schema
from .spec import Spec


def get_uri_filter(app):
    """
    Return a filter function that takes a URI and returns whether it should
    be filter out from the swagger documentation or not.

    Arguments:
        app: The application to take `config.API_URI_FILTER` from. Possible
             values for this config option are: `slash` (to keep URIs that
             end with a `/`), `all` (to keep all URIs). All other values
             default to keep all URIs that don't end with a `/`.

    Returns:
        `True` if the URI should be *filtered out* from the swagger
        documentation, and `False` if it should be kept in the documentation.
    """
    choice = getattr(app.config, "API_URI_FILTER", None)

    if choice == "slash":
        # Keep URIs that end with a /.
        return lambda uri: not uri.endswith("/")

    if choice == "all":
        # Keep all URIs.
        return lambda uri: False

    # Keep URIs that don't end with a /, (special case: "/").
    return lambda uri: len(uri) > 1 and uri.endswith("/")


def remove_nulls(dictionary, deep=True):
    """
    Removes all null values from a dictionary.
    """
    return {
        k: remove_nulls(v, deep) if deep and type(v) is dict else v
        for k, v in dictionary.items()
        if v is not None
    }


def build_consumer_route_param(consumer) -> Dict:
    spec = serialize_schema(consumer.field)
    if "properties" in spec:
        for name, prop_spec in spec["properties"].items():
            route_param = {
                **prop_spec,
                "required": consumer.required,
                "in": consumer.location,
                "name": name,
            }
    else:
        route_param = {
            **spec,
            "required": consumer.required,
            "in": consumer.location,
            "name": consumer.field.name if hasattr(consumer.field, "name") else "body",
        }

    if "$ref" in route_param:
        route_param["schema"] = {"$ref": route_param["$ref"]}
        del route_param["$ref"]

    return route_param


def build_method(app: Sanic, handler, method: str, route, route_specs: Dict) -> Dict:
    if hasattr(handler, "view_class"):
        view_handler = getattr(handler.view_class, method.lower())
        route_spec = route_specs.get(view_handler)
    else:
        route_spec = route_specs.get(handler)

    if method == "OPTIONS" or route_spec.exclude:
        return

    api_consumes_content_types = getattr(
        app.config, "API_CONSUMES_CONTENT_TYPES", ["application/json"]
    )
    consumes_content_types = (
        route_spec.consumes_content_type or api_consumes_content_types
    )

    api_produces_content_types = getattr(
        app.config, "API_PRODUCES_CONTENT_TYPES", ["application/json"]
    )
    produces_content_types = (
        route_spec.produces_content_type or api_produces_content_types
    )

    # Parameters - Path & Query String
    route_parameters = []
    for parameter in route.parameters:
        route_parameters.append(
            {
                **serialize_schema(parameter.cast),
                "required": True,
                "in": "path",
                "name": parameter.name,
            }
        )

    for consumer in route_spec.consumes:
        route_param = build_consumer_route_param(consumer=consumer)
        route_parameters.append(route_param)

    responses = {}

    if len(route_spec.response) == 0:
        responses["200"] = {
            "schema": serialize_schema(route_spec.produces.field)
            if route_spec.produces
            else None,
            "description": route_spec.produces.description
            if route_spec.produces
            else None,
        }

    for (status_code, routefield) in route_spec.response:
        responses["{}".format(status_code)] = {
            "schema": serialize_schema(routefield.field),
            "description": routefield.description,
        }

    return remove_nulls(
        {
            "operationId": route_spec.operation or route.name,
            "summary": route_spec.summary,
            "description": route_spec.description,
            "consumes": consumes_content_types,
            "produces": produces_content_types,
            "tags": route_spec.tags or None,
            "parameters": route_parameters,
            "responses": responses,
        }
    )


def build_paths(app: Sanic, url_prefix: str, route_specs: Dict) -> Dict:
    paths = {}
    uri_filter = get_uri_filter(app)

    for uri, route in app.router.routes_all.items():

        # Ignore routes under swagger blueprint
        if route.uri.startswith(url_prefix):
            continue

        # Apply the URI filter
        if uri_filter(uri):
            continue

        # route.name will be None when using class based view
        if route.name and "static" in route.name:
            # TODO: add static flag in sanic routes
            continue

        # --------------------------------------------------------------- #
        # Methods
        # --------------------------------------------------------------- #

        # Build list of methods and their handler functions
        if isinstance(route.handler, CompositionView):
            view = route.handler
            method_handlers = view.handlers.items()
        else:
            method_handlers = zip(route.methods, repeat(route.handler))

        methods = {}
        for method, handler in method_handlers:
            _method = build_method(
                app=app,
                handler=handler,
                method=method,
                route=route,
                route_specs=route_specs,
            )
            if _method:
                methods[method.lower()] = _method

        uri_parsed = uri
        for parameter in route.parameters:
            uri_parsed = re.sub(
                "<" + parameter.name + ".*?>", "{" + parameter.name + "}", uri_parsed
            )

        if methods:
            paths[uri_parsed] = methods

    return paths


def build_blueprint(app, route_specs: Dict) -> None:

    for blueprint in app.blueprints.values():
        for route in blueprint.routes:
            if hasattr(route.handler, "view_class"):
                # class based view
                view = route.handler.view_class
                for http_method in route.methods:
                    _handler = getattr(view, http_method.lower(), None)
                    if _handler:
                        route_spec = route_specs.get(_handler)
                        route_spec.blueprint = blueprint
                        if not route_spec.tags:
                            route_spec.tags.append(blueprint.name)
            else:
                route_spec = route_specs.get(route.handler)
                route_spec.blueprint = blueprint
                if not route_spec.tags:
                    route_spec.tags.append(blueprint.name)
        return

    if hasattr(app, "router"):
        for name, value in app.router.routes_names.items():

            # TODO: Is this correct that the tags get the name of the app
            if not name:
                name = app.name

            endpoint, route = value
            if isinstance(route.handler, CompositionView):
                # class based view
                for http_method, _handler in route.handler.handlers.items():
                    if _handler:
                        route_spec = route_specs.get(_handler)
                        route_spec.name = name
                        if not route_spec.tags:
                            route_spec.tags.append(name)
            else:
                route_spec = route_specs.get(route.handler)
                route_spec.name = name


def add_routes(
    app: Sanic,
    url_prefix: str,
    spec: Dict,
    dir_path: str,
    route_specs: Dict,
    definitions: Dict,
) -> None:

    # Redirect "/swagger" to "/swagger/"
    @app.route(url_prefix, strict_slashes=True)
    def __index(request):
        return response.redirect("{}/".format(url_prefix))

    app.static(url_prefix + "/", dir_path + "/index.html", strict_slashes=True)
    app.static(url_prefix + "/", dir_path)

    @app.listener("after_server_start")
    def __build_spec(app, loop):
        _spec = Spec(app=app)

        # --------------------------------------------------------------- #
        # Blueprint Tags
        # --------------------------------------------------------------- #

        build_blueprint(app=app, route_specs=route_specs)

        paths = build_paths(app=app, url_prefix=url_prefix, route_specs=route_specs)

        # --------------------------------------------------------------- #
        # Definitions
        # --------------------------------------------------------------- #

        _spec.add_definitions(
            definitions={
                obj.object_name: definition for obj, definition in definitions.values()
            }
        )

        # --------------------------------------------------------------- #
        # Tags
        # --------------------------------------------------------------- #

        # TODO: figure out how to get descriptions in these
        tags = {}
        for route_spec in route_specs.values():
            for tag in route_spec.tags:
                # filter out swagger internal routes
                if tag.startswith("__"):
                    continue
                tags[tag] = True
        _spec.add_tags(tags=[{"name": name} for name in tags.keys()])

        _spec.add_paths(paths)
        app._spec = _spec

    @app.route(url_prefix + "/swagger.json")
    @route_specs.route(exclude=True)
    def __spec(request):
        print(1)
        for k, v in app._spec.__dict__.items():
            print('ww')
            print(k)
            print(v)
            print('ee')
        print(2)
        return response.json(app._spec)

    @app.route(url_prefix + "/swagger-config")
    def __config(request):
        options = {}

        if hasattr(request.app.config, "SWAGGER_UI_CONFIGURATION"):
            options = getattr(request.app.config, "SWAGGER_UI_CONFIGURATION")

        return response.json(options)


class Swagger:
    def __init__(self, app: Sanic, url_prefix=None, spec=None):
        self.app = app
        self.url_prefix = url_prefix or "/swagger"
        _dir_path = os.path.dirname(os.path.realpath(__file__))
        self.dir_path = os.path.abspath(_dir_path + "/ui")
        self.definitions = {}
        self.spec = spec or Spec(app=app)
        self.doc = RouteSpecs()
        self._init()

    def _init(self) -> None:
        add_routes(
            app=self.app,
            url_prefix=self.url_prefix,
            spec=self.spec,
            dir_path=self.dir_path,
            route_specs=self.doc,
            definitions=self.definitions,
        )
