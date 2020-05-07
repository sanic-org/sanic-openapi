import os
import re
from itertools import repeat

from sanic.blueprints import Blueprint
from sanic.response import json, redirect
from sanic.views import CompositionView

from .doc import RouteSpec, definitions
from .doc import route as doc_route
from .doc import route_specs, serialize_schema
from .spec import Spec

swagger_blueprint = Blueprint("swagger", url_prefix="/swagger")

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(dir_path + "/ui")


# Redirect "/swagger" to "/swagger/"
@swagger_blueprint.route("", strict_slashes=True)
def index(request):
    return redirect("{}/".format(swagger_blueprint.url_prefix))


swagger_blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
swagger_blueprint.static("/", dir_path)


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


@swagger_blueprint.listener("after_server_start")
def build_spec(app, loop):
    _spec = Spec(app=app)

    # --------------------------------------------------------------- #
    # Blueprint Tags
    # --------------------------------------------------------------- #

    for blueprint in app.blueprints.values():
        if hasattr(blueprint, "routes"):
            for route in blueprint.routes:
                if hasattr(route.handler, "view_class"):
                    # class based view
                    view = route.handler.view_class
                    for http_method in route.methods:
                        _handler = getattr(view, http_method.lower(), None)
                        if _handler:
                            route_spec = route_specs[_handler]
                            route_spec.blueprint = blueprint
                            if not route_spec.tags:
                                route_spec.tags.append(blueprint.name)
                else:
                    route_spec = route_specs[route.handler]
                    route_spec.blueprint = blueprint
                    if not route_spec.tags:
                        route_spec.tags.append(blueprint.name)

    paths = {}
    uri_filter = get_uri_filter(app)

    for uri, route in app.router.routes_all.items():

        # Ignore routes under swagger blueprint
        if route.uri.startswith(swagger_blueprint.url_prefix):
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
        handler_type = type(route.handler)
        if handler_type is CompositionView:
            view = route.handler
            method_handlers = view.handlers.items()
        else:
            method_handlers = zip(route.methods, repeat(route.handler))

        methods = {}
        for _method, _handler in method_handlers:
            if hasattr(_handler, "view_class"):
                view_handler = getattr(_handler.view_class, _method.lower())
                route_spec = route_specs.get(view_handler) or RouteSpec()
            else:
                route_spec = route_specs.get(_handler) or RouteSpec()

            if _method == "OPTIONS" or route_spec.exclude:
                continue

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
                        "name": consumer.field.name
                        if not isinstance(consumer.field, type)
                        and hasattr(consumer.field, "name")
                        else "body",
                    }

                if "$ref" in route_param:
                    route_param["schema"] = {"$ref": route_param["$ref"]}
                    del route_param["$ref"]

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

            endpoint = remove_nulls(
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

            methods[_method.lower()] = endpoint

        uri_parsed = uri
        for parameter in route.parameters:
            uri_parsed = re.sub(
                "<" + parameter.name + ".*?>", "{" + parameter.name + "}", uri_parsed
            )

        if methods:
            paths[uri_parsed] = methods

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
        if route_spec.blueprint and route_spec.blueprint.name in ("swagger"):
            # TODO: add static flag in sanic routes
            continue
        for tag in route_spec.tags:
            tags[tag] = True
    _spec.add_tags(tags=[{"name": name} for name in tags.keys()])

    _spec.add_paths(paths)
    swagger_blueprint._spec = _spec


@swagger_blueprint.route("/swagger.json")
@doc_route(exclude=True)
def spec(request):
    return json(swagger_blueprint._spec.as_dict)


@swagger_blueprint.route("/swagger-config")
def config(request):
    options = {}

    if hasattr(request.app.config, "SWAGGER_UI_CONFIGURATION"):
        options = getattr(request.app.config, "SWAGGER_UI_CONFIGURATION")

    return json(options)
