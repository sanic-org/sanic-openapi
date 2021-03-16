import re
from itertools import repeat
from os.path import abspath, dirname, realpath

from sanic.blueprints import Blueprint
from sanic.response import json, redirect
from sanic.views import CompositionView

from ..doc import route as doc_route
from ..utils import get_uri_filter
from . import operations, specification


def blueprint_factory():
    oas3_blueprint = Blueprint("openapi", url_prefix="/swagger")

    dir_path = dirname(dirname(realpath(__file__)))
    dir_path = abspath(dir_path + "/ui")

    oas3_blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
    oas3_blueprint.static("/", dir_path)

    # Redirect "/swagger" to "/swagger/"
    @oas3_blueprint.route("", strict_slashes=True)
    def index(request):
        return redirect("{}/".format(oas3_blueprint.url_prefix))

    @oas3_blueprint.route("/swagger.json")
    @doc_route(exclude=True)
    def spec(request):
        return json(specification.build().serialize())

    @oas3_blueprint.route("/swagger-config")
    def config(request):
        return json(getattr(request.app.config, "SWAGGER_UI_CONFIGURATION", {}))

    @oas3_blueprint.listener("before_server_start")
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
            host = getattr(app.config, "API_HOST", None)
            basePath = getattr(app.config, "API_BASEPATH", "")
            if host is None or basePath is None:
                continue

            specification.url(f"{scheme}://{host}/{basePath}")

        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, "routes"):
                continue

            for _route in _blueprint.routes:
                if hasattr(_route.handler, "view_class"):
                    # class based view
                    for http_method in _route.methods:
                        _handler = getattr(_route.handler.view_class, http_method.lower(), None)
                        if _handler:
                            operation = operations[_route.handler]
                            if not operation.tags:
                                operation.tag(_blueprint.name)
                else:
                    operation = operations[_route.handler]
                    # operation.blueprint = _blueprint
                    # is this necc ?
                    if not operation.tags:
                        operation.tag(_blueprint.name)

        uri_filter = get_uri_filter(app)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for _uri, _route in app.router.routes_all.items():

            # Ignore routes under swagger blueprint
            if _route.uri.startswith(oas3_blueprint.url_prefix):
                continue

            # Apply the URI filter
            if uri_filter(_uri):
                continue

            # route.name will be None when using class based view
            if _route.name and "static" in _route.name:
                continue

            # --------------------------------------------------------------- #
            # Methods
            # --------------------------------------------------------------- #

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

                if method == "OPTIONS":
                    continue

                operation = operations[_handler]

                if not hasattr(operation, "operationId"):
                    operation.operationId = "%s_%s" % (method.lower(), _route.name)

                for _parameter in _route.parameters:
                    operation.parameter(_parameter.name, _parameter.cast, "path")

                specification.operation(uri, method, operation)

    return oas3_blueprint
