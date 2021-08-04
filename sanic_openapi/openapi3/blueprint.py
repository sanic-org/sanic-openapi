import inspect
from os.path import abspath, dirname, realpath

from sanic.blueprints import Blueprint
from sanic.response import json, redirect

from ..utils import get_all_routes, get_blueprinted_routes
from . import operations, specification

DEFAULT_SWAGGER_UI_CONFIG = {
    "apisSorter": "alpha",
    "operationsSorter": "alpha",
}


def blueprint_factory():
    oas3_blueprint = Blueprint("openapi", url_prefix="/swagger")

    dir_path = dirname(dirname(realpath(__file__)))
    dir_path = abspath(dir_path + "/ui")

    oas3_blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
    oas3_blueprint.static("", dir_path)

    # Redirect "/swagger" to "/swagger/"
    @oas3_blueprint.route("", strict_slashes=True)
    def index(request):
        return redirect("{}/".format(oas3_blueprint.url_prefix))

    @oas3_blueprint.route("/swagger.json")
    def spec(request):
        return json(specification.build().serialize())

    @oas3_blueprint.route("/swagger-config")
    def config(request):
        return json(
            getattr(
                request.app.config,
                "SWAGGER_UI_CONFIGURATION",
                DEFAULT_SWAGGER_UI_CONFIG,
            )
        )

    @oas3_blueprint.listener("before_server_start")
    def build_spec(app, loop):
        # --------------------------------------------------------------- #
        # Blueprint Tags
        # --------------------------------------------------------------- #

        for blueprint_name, handler in get_blueprinted_routes(app):
            operation = operations[handler]
            if not operation.tags:
                operation.tag(blueprint_name)

        # --------------------------------------------------------------- #
        # Operations
        # --------------------------------------------------------------- #
        for (
            uri,
            route_name,
            route_parameters,
            method_handlers,
        ) in get_all_routes(app, oas3_blueprint.url_prefix):

            # --------------------------------------------------------------- #
            # Methods
            # --------------------------------------------------------------- #

            uri = uri if uri == "/" else uri.rstrip("/")

            for method, _handler in method_handlers:

                if method == "OPTIONS":
                    continue

                if hasattr(_handler, "view_class"):
                    _handler = getattr(_handler.view_class, method.lower())
                operation = operations[_handler]

                if operation._exclude:
                    continue

                docstring = inspect.getdoc(_handler)

                if docstring:
                    operation.autodoc(docstring)

                # operation ID must be unique, and it isnt currently used for
                # anything in UI, so dont add something meaningless
                # if not hasattr(operation, "operationId"):
                #     operation.operationId = "%s_%s" % (
                #       method.lower(), route.name
                #     )

                for _parameter in route_parameters:
                    operation.parameter(
                        _parameter.name, _parameter.cast, "path"
                    )

                specification.operation(uri, method, operation)

        add_static_info_to_spec_from_config(app, specification)

    return oas3_blueprint


def add_static_info_to_spec_from_config(app, specification):
    """
    Reads app.config and sets attributes to specification according to the
    desired values.

    Modifies specification in-place and returns None
    """
    specification._do_describe(
        getattr(app.config, "API_TITLE", "API"),
        getattr(app.config, "API_VERSION", "1.0.0"),
        getattr(app.config, "API_DESCRIPTION", None),
        getattr(app.config, "API_TERMS_OF_SERVICE", None),
    )

    specification._do_license(
        getattr(app.config, "API_LICENSE_NAME", None),
        getattr(app.config, "API_LICENSE_URL", None),
    )

    specification._do_contact(
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
