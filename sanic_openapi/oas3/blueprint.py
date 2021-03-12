import re
from itertools import repeat
from os.path import abspath, dirname, realpath

from sanic.blueprints import Blueprint
from sanic.response import json, redirect
from sanic.views import CompositionView

from ..doc import route as doc_route
from . import operations
from .definitions import PathItem, Tag
from .spec import Spec as Swagger3Spec


def blueprint_factory():
    blueprint = Blueprint("openapi", url_prefix="/openapi")

    dir_path = dirname(dirname(realpath(__file__)))
    dir_path = abspath(dir_path + "/ui")
    blueprint.static("/", dir_path + "/index.html", strict_slashes=True)
    blueprint.static("/", dir_path)

    @blueprint.route("", strict_slashes=True)
    def index(request):
        return redirect("{}/".format(blueprint.url_prefix))

    @blueprint.route("/swagger-config")
    def config(request):
        options = {}

        if hasattr(request.app.config, "SWAGGER_UI_CONFIGURATION"):
            options = getattr(request.app.config, "SWAGGER_UI_CONFIGURATION")

        return json(options)

    @blueprint.listener("before_server_start")
    def build_spec(app, loop):
        # --------------------------------------------------------------- #
        # Globals
        # --------------------------------------------------------------- #
        _spec = Swagger3Spec(app=app)
        # --------------------------------------------------------------- #
        # Blueprints
        # --------------------------------------------------------------- #
        for _blueprint in app.blueprints.values():
            if not hasattr(_blueprint, "routes"):
                continue

            for _route in _blueprint.routes:
                if _route.handler not in operations:
                    continue

                operation = operations[_route.handler]

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

                for _tag in operation.tags:
                    if _tag not in _spec._tags.keys():
                        _spec._tags[_tag] = Tag(_tag)

                _spec._paths[uri][method.lower()] = operation

        _spec.tags = [_spec._tags[k] for k in _spec._tags]

        paths = {}

        for path, operation in _spec._paths.items():
            paths[path] = PathItem(**{k: v.build() for k, v in operation.items()})

        _spec.paths = paths

        blueprint._spec = _spec

    @blueprint.route("/swagger.json")
    @doc_route(exclude=True)
    def spec(request):
        return json(blueprint._spec.as_dict)

    return blueprint
