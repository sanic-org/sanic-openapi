import re

from itertools import repeat
from sanic.blueprints import Blueprint
from sanic.response import json, redirect
from sanic.views import CompositionView
from os.path import dirname, realpath, abspath
from .builders import ComponentsBuilder, OperationsBuilder, SpecificationBuilder
from ..doc import route as doc_route
from yaml import safe_dump as yaml_dump
from . import operations, specification


def blueprint_factory_bis():
    blueprint = Blueprint("openapi", url_prefix="/openapi")
    dir_path = dirname(dirname(realpath(__file__)))
    dir_path = abspath(dir_path + "/ui")
    blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
    blueprint.static("/", dir_path)

    @blueprint.route("", strict_slashes=True)
    def index(request):
        return redirect("{}/".format(blueprint.url_prefix))

    @blueprint.route("/openapi.json")
    @doc_route(exclude=True)
    def spec(request):
        return json({"robi": "polli"})

    @blueprint.route("/openapi.yaml")
    @doc_route(exclude=True)
    def spec(request):
        return yaml_dump({"robi": "polli"}, indent=2)

    return blueprint


def blueprint_factory():
    blueprint = Blueprint("openapi", url_prefix="/openapi")

    dir_path = dirname(dirname(realpath(__file__)))
    dir_path = abspath(dir_path + "/ui")
    blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
    blueprint.static("/", dir_path)

    @blueprint.route("", strict_slashes=True)
    def index(request):
        return redirect("{}/".format(blueprint.url_prefix))

    @blueprint.route("/openapi.json")
    @doc_route(exclude=True)
    def spec(request):
        openapi = specification.build().serialize()
        return json(openapi)

    @blueprint.listener("before_server_start")
    def build_spec(app, loop):
        # --------------------------------------------------------------- #
        # Globals
        # --------------------------------------------------------------- #
        specification.describe(
            getattr(app.config, "API_TITLE", "API"),
            getattr(app.config, "API_VERSION", "1.0.0"),
            getattr(app.config, "API_DESCRIPTION", None),
            getattr(app.config, "API_TERMS_OF_SERVICE", None),
        )

        specification.license(
            getattr(app.config, "API_LICENSE_NAME", None),
            getattr(app.config, "API_LICENSE_URL", None),
        )

        specification.contact(
            getattr(app.config, "API_CONTACT_NAME", None),
            getattr(app.config, "API_CONTACT_URL", None),
            getattr(app.config, "API_CONTACT_EMAIL", None),
        )

        for scheme in getattr(app.config, "API_SCHEMES", ["http"]):
            host = getattr(app.config, "API_HOST", "localhost")
            if not host:
                continue

            basePath = getattr(app.config, "API_BASEPATH", "")
            if basePath is None:
                continue

            specification.url(f"{scheme}://{host}/{basePath}")

        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, "routes"):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in operations:
                    continue

                operation = operations.get(_route.handler)

                if not operation.tags:
                    operation.tag(_blueprint.name)

        return

    return blueprint

    def _(app, loop):
        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, "routes"):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in operations:
                    continue

                operation = operations.get(_route.handler)

                if not operation.tags:
                    operation.tag(_blueprint.name)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for _uri, _route in app.router.routes_all.items():
            if "<file_uri" in _uri:
                continue

            handler_type = type(_route.handler)

            if handler_type is CompositionView:
                view = _route.handler
                method_handlers = view.handlers.items()
            else:
                method_handlers = zip(_route.methods, repeat(_route.handler))

            uri = _uri if _uri == "/" else _uri.rstrip("/")

            for segment in _route.parameters:
                uri = re.sub("<" + segment.name + ".*?>", "{" + segment.name + "}", uri)

            for method, _handler in method_handlers:
                if _handler not in operations:
                    continue

                operation = operations[_handler]

                if not hasattr(operation, "operationId"):
                    operation.operationId = "%s_%s" % (method.lower(), _route.name)

                for _parameter in _route.parameters:
                    operation.parameter(_parameter.name, _parameter.cast, "path")

                specification.operation(uri, method, operation)

        return blueprint
