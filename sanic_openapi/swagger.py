import os
import re
from itertools import repeat
from typing import Dict

from sanic import Sanic, response
from sanic.views import CompositionView

from .doc import serialize_schema
from .route_specs import RouteSpecs
from .spec import Spec


class Swagger:
    def __init__(self, app: Sanic, url_prefix=None, spec=None):
        self.app = app
        self.url_prefix = url_prefix or "/swagger"
        _dir_path = os.path.dirname(os.path.realpath(__file__))
        self.dir_path = os.path.abspath(_dir_path + "/ui")
        self.spec = spec or Spec(config=app.config)
        self.doc = RouteSpecs(spec=self.spec)
        self.paths = {}
        self._init()
        self.blueprint_info = {}

    def _init(self) -> None:
        # Redirect "/swagger" to "/swagger/"
        @self.app.route(self.url_prefix, strict_slashes=True)
        def __index(request):
            return response.redirect("{}/".format(self.url_prefix))

        self.app.static(
            self.url_prefix + "/", self.dir_path + "/index.html", strict_slashes=True
        )
        self.app.static(self.url_prefix + "/", self.dir_path)

        @self.app.listener("after_server_start")
        def __build_spec(*args):

            # --------------------------------------------------------------- #
            # Blueprint Tags
            # --------------------------------------------------------------- #

            self.build_blueprints()

            self.paths = self.build_paths(
                routes_all=self.app.router.routes_all,
                uri_filter=get_uri_filter(self.app)
            )

            # --------------------------------------------------------------- #
            # Definitions
            # --------------------------------------------------------------- #

            # --------------------------------------------------------------- #
            # Tags
            # --------------------------------------------------------------- #

            # TODO: figure out how to get descriptions in these
            tags = {}
            for route_spec in self.doc.values():
                for tag in route_spec.tags:
                    # filter out swagger internal routes
                    if tag.startswith("__"):
                        continue
                    tags[tag] = True
            self.spec.add_tags(tags=[{"name": name} for name in tags.keys()])

            self.spec.add_paths(self.paths)

        @self.app.route(self.url_prefix + "/swagger.json")
        @self.doc.route(exclude=True)
        def __spec(request):
            return response.json(self.spec.as_dict)

        @self.app.route(self.url_prefix + "/swagger-config")
        def __config(request):
            options = {}

            if hasattr(request.app.config, "SWAGGER_UI_CONFIGURATION"):
                options = getattr(request.app.config, "SWAGGER_UI_CONFIGURATION")

            return response.json(options)

    # Blueprints

    def build_blueprints(self) -> None:

        all_blueprints = self.app.blueprints

        for blueprint in all_blueprints.values():
            for route in blueprint.routes:
                if hasattr(route.handler, "view_class"):
                    self.handle_blueprint_class(blueprint, route)
                else:
                    self.blueprint_from_handler(blueprint.name, route.handler)
            return

        if hasattr(self.app, "router"):
            self.blueprint_has_router()

    def handle_blueprint_class(self, blueprint, route):
        # class based view
        view = route.handler.view_class
        for http_method in route.methods:
            handler = getattr(view, http_method.lower(), None)
            self.blueprint_from_handler(blueprint.name, handler)

    def blueprint_has_router(self):
        for name, value in self.app.router.routes_names.items():

            # TODO: Is this correct that the tags get the name of the app
            if not name:
                name = self.app.name

            endpoint, route = value
            if isinstance(route.handler, CompositionView):
                # class based view
                for http_method, handler in route.handler.handlers.items():
                    self.blueprint_from_handler(name, handler)
            else:
                # should this not also get tags by using blueprint_from_handler?
                route_spec = self.doc.get(route.handler)
                route_spec.name = name

    def blueprint_from_handler(self, name, handler):
        if handler:
            route_spec = self.doc.get(handler)
            route_spec.name = name
            if not route_spec.tags:
                route_spec.tags.append(name)

    # Paths

    def build_paths(self, routes_all, uri_filter) -> Dict:
        paths = {}

        for uri, route in routes_all.items():

            # Ignore routes under swagger blueprint
            if route.uri.startswith(self.url_prefix):
                continue

            # Apply the URI filter
            if uri_filter(uri):
                continue

            # route.name will be None when using class based view
            if route.name and "static" in route.name:
                # TODO: add static flag in sanic routes
                continue

            uri, methods = build_path(self.app.config, uri, route, self.doc)
            if methods:
                paths[uri] = methods

        return paths


def build_path(app_config, uri, route, doc):
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
        if hasattr(handler, "view_class"):
            view_handler = getattr(handler.view_class, method.lower())
            route_spec = doc.get(view_handler)
        else:
            route_spec = doc.get(handler)

        _method = build_method(
            app_config=app_config, route_spec=route_spec, method=method, route=route
        )
        if _method:
            methods[method.lower()] = _method

    uri_parsed = uri
    for parameter in route.parameters:
        uri_parsed = re.sub(
            "<" + parameter.name + ".*?>", "{" + parameter.name + "}", uri_parsed
        )

    return uri_parsed, methods


def build_method(app_config, route_spec, method: str, route) -> Dict:

    if method == "OPTIONS" or route_spec.exclude:
        return

    api_consumes_content_types = getattr(
        app_config, "API_CONSUMES_CONTENT_TYPES", ["application/json"]
    )
    consumes_content_types = (
        route_spec.consumes_content_type or api_consumes_content_types
    )

    api_produces_content_types = getattr(
        app_config, "API_PRODUCES_CONTENT_TYPES", ["application/json"]
    )
    produces_content_types = (
        route_spec.produces_content_type or api_produces_content_types
    )

    route_parameters = build_parameters(route, route_spec)

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


def build_parameters(route, route_spec):
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
    return route_parameters


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
