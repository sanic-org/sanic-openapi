import os
import re
from itertools import repeat
from typing import Dict

from sanic import Sanic, response
from sanic.views import CompositionView

from .doc import RouteSpecs, serialize_schema
from .spec import Spec


class Swagger:
    def __init__(self, app: Sanic, url_prefix=None, spec=None):
        self.app = app
        self.url_prefix = url_prefix or "/swagger"
        _dir_path = os.path.dirname(os.path.realpath(__file__))
        self.dir_path = os.path.abspath(_dir_path + "/ui")
        self.definitions = {}
        self.spec = spec or Spec(config=app.config)
        self.doc = RouteSpecs(spec=self.spec)
        self.paths = {}
        self._init()

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

            self.build_blueprint()

            self.build_paths()

            # --------------------------------------------------------------- #
            # Definitions
            # --------------------------------------------------------------- #

            self.spec.add_definitions(
                definitions={
                    obj.object_name: definition
                    for obj, definition in self.definitions.values()
                }
            )

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

    def build_blueprint(self) -> None:

        for blueprint in self.app.blueprints.values():
            for route in blueprint.routes:
                if hasattr(route.handler, "view_class"):
                    # class based view
                    view = route.handler.view_class
                    for http_method in route.methods:
                        _handler = getattr(view, http_method.lower(), None)
                        if _handler:
                            route_spec = self.doc.get(_handler)
                            route_spec.blueprint = blueprint
                            if not route_spec.tags:
                                route_spec.tags.append(blueprint.name)
                else:
                    route_spec = self.doc.get(route.handler)
                    route_spec.blueprint = blueprint
                    if not route_spec.tags:
                        route_spec.tags.append(blueprint.name)
            return

        if hasattr(self.app, "router"):
            self.blueprint_has_router()

    def blueprint_has_router(self):
        for name, value in self.app.router.routes_names.items():

            # TODO: Is this correct that the tags get the name of the app
            if not name:
                name = self.app.name

            endpoint, route = value
            if isinstance(route.handler, CompositionView):
                # class based view
                for http_method, _handler in route.handler.handlers.items():
                    if _handler:
                        route_spec = self.doc.get(_handler)
                        route_spec.name = name
                        if n

@AtomsForPeace
Sorry for no-response in recent days.

This PR is a remarkable work for this project. I appreciated your contribution.
I skipped a test due to the global variable issue. Would you mind to enable this test to verify this PR?

sanic-openapi/tests/test_fields.py

Line 405 in 3cdf880
 @pytest.mark.skip(reason="Failed due to global variables.") 

And because this PR also changes the usage of this project, maybe we can put the __version__ to 0.7.0. What do you think?
ot route_spec.tags:
                            route_spec.tags.append(name)
            else:
                route_spec = self.doc.get(route.handler)
                route_spec.name = name

    def build_paths(self) -> Dict:
        uri_filter = get_uri_filter(self.app)

        for uri, route in self.app.router.routes_all.items():

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
                _method = self.build_method(
                    handler=handler, method=method, route=route,
                )
                if _method:
                    methods[method.lower()] = _method

            uri_parsed = uri
            for parameter in route.parameters:
                uri_parsed = re.sub(
                    "<" + parameter.name + ".*?>",
                    "{" + parameter.name + "}",
                    uri_parsed,
                )

            if methods:
                self.paths[uri_parsed] = methods

    def build_method(self, handler, method: str, route) -> Dict:
        if hasattr(handler, "view_class"):
            view_handler = getattr(handler.view_class, method.lower())
            route_spec = self.doc.get(view_handler)
        else:
            route_spec = self.doc.get(handler)

        if method == "OPTIONS" or route_spec.exclude:
            return

        api_consumes_content_types = getattr(
            self.app.config, "API_CONSUMES_CONTENT_TYPES", ["application/json"]
        )
        consumes_content_types = (
            route_spec.consumes_content_type or api_consumes_content_types
        )

        api_produces_content_types = getattr(
            self.app.config, "API_PRODUCES_CONTENT_TYPES", ["application/json"]
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
