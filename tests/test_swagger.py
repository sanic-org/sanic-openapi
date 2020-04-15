import pytest
from sanic import Blueprint
from sanic.constants import HTTP_METHODS
from sanic.response import text
from sanic.views import CompositionView, HTTPMethodView

METHODS = [method.lower() for method in HTTP_METHODS]


class SimpleView(HTTPMethodView):
    def get(self, request):
        return text("I am get method")

    def post(self, request):
        return text("I am post method")

    def put(self, request):
        return text("I am put method")

    def patch(self, request):
        return text("I am patch method")

    def delete(self, request):
        return text("I am delete method")

    def head(self, request):
        return text("I am head method")

    def options(self, request):
        return text("I am options method")


def get_handler(request):
    return text("I am a get method")


view = CompositionView()
view.add(["GET"], get_handler)
view.add(["POST", "PUT"], lambda request: text("I am a post/put method"))


def test_swagger_endpoint(app_with_swagger):
    _, response = app_with_swagger.test_client.get("/swagger/")
    assert response.status == 200
    assert response.content_type == "text/html"


def test_swagger_json(app_with_swagger):
    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json.get("swagger") == "2.0"
    assert swagger_json.get("definitions") == {}
    assert swagger_json.get("tags") == []
    assert swagger_json.get("paths") == {}


@pytest.mark.parametrize("method", METHODS)
def test_document_route(app_with_swagger, method):
    @app_with_swagger.route("/", methods=[method])
    def test(request):
        return text("test")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"] == {
        "/": {
            method: {
                "operationId": "test",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "parameters": [],
                "responses": {"200": {}},
            }
        }
    }


@pytest.mark.parametrize("method", METHODS)
def test_document_blueprint_route(app_with_swagger, swagger, method):

    bp = Blueprint("test")

    @bp.route("/", methods=[method])
    def test(request):
        return text("test")

    app_with_swagger.blueprint(bp)

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json

    assert {"name": "test"} in swagger_json["tags"]
    assert swagger_json["paths"] == {
        "/": {
            method: {
                "operationId": "test.test",
                "consumes": ["application/json"],
                "produces": ["application/json"],
                "tags": ["test"],
                "parameters": [],
                "responses": {"200": {}},
            }
        }
    }


def test_class_based_view(app_with_swagger):
    """
    In sanic_openapi/swagger.py#n124, class based view will not document endpoint with
    options method.
    """
    app_with_swagger.add_route(SimpleView.as_view(), "/")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    methods = METHODS.copy()
    methods.remove("options")

    assert sorted(set(methods)) == sorted(set(swagger_json["paths"]["/"].keys()))


def test_blueprint_class_based_view(app_with_swagger):

    bp = Blueprint("test")
    bp.add_route(SimpleView.as_view(), "/")
    app_with_swagger.blueprint(bp)

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    methods = METHODS.copy()
    methods.remove("options")

    assert sorted(set(methods)) == sorted(set(swagger_json["paths"]["/"].keys()))
    assert {"name": "test"} in swagger_json["tags"]


def test_document_compositionview(app_with_swagger):
    app_with_swagger.add_route(view, "/")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert set(swagger_json["paths"]["/"].keys()) == set(["get", "post", "put"])
    assert {"name": "test"} in swagger_json["tags"]


@pytest.mark.xfail(reason="Not support now.")
def test_document_blueprint_compositionview(app_with_swagger):

    bp = Blueprint("test")
    bp.add_route(view, "/")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert set(swagger_json["paths"]["/"].keys()) == set(["get", "post", "put"])


def test_swagger_ui_config(app_with_swagger):

    _, response = app_with_swagger.test_client.get("/swagger/swagger-config")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_config = response.json
    assert swagger_config == {}

    swagger_ui_configuration = {
        "validatorUrl": None,  # Disable Swagger validator
        "displayRequestDuration": True,
        "docExpansion": "full",
    }
    app_with_swagger.config.SWAGGER_UI_CONFIGURATION = swagger_ui_configuration

    _, response = app_with_swagger.test_client.get("/swagger/swagger-config")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_config = response.json
    assert swagger_config == swagger_ui_configuration


@pytest.mark.parametrize(
    "configs",
    [
        {
            "API_HOST": "http://0.0.0.0",
            "API_BASEPATH": "/api",
            "API_VERSION": "0.1.0",
            "API_TITLE": "Sanic OpenAPI test",
            "API_DESCRIPTION": "The API doc",
            "API_TERMS_OF_SERVICE": "Use with caution!",
            "API_CONTACT_EMAIL": "foo@bar.com",
            "API_LICENSE_NAME": "MIT",
            "API_LICENSE_URL": "https://choosealicense.com/licenses/mit/",
        },
        {
            "API_HOST": "http://test.sanic-openapi",
            "API_BASEPATH": "/api_test",
            "API_VERSION": None,
            "API_TITLE": None,
            "API_DESCRIPTION": None,
            "API_TERMS_OF_SERVICE": None,
            "API_CONTACT_EMAIL": None,
            "API_LICENSE_NAME": None,
            "API_LICENSE_URL": None,
        },
    ],
)
def test_configs(app_with_swagger, configs):

    app_with_swagger.config.update(configs)

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["host"] == configs["API_HOST"]
    assert swagger_json["basePath"] == configs["API_BASEPATH"]

    info = swagger_json.get("info")
    assert isinstance(info, dict)
    assert info["version"] == configs["API_VERSION"]
    assert info["title"] == configs["API_TITLE"]
    assert info["description"] == configs["API_DESCRIPTION"]
    assert info["termsOfService"] == configs["API_TERMS_OF_SERVICE"]
    assert info["contact"]["email"] == configs["API_CONTACT_EMAIL"]
    assert info["license"]["name"] == configs["API_LICENSE_NAME"]
    assert info["license"]["url"] == configs["API_LICENSE_URL"]


def test_skip_static_file(app_with_swagger):
    app_with_swagger.static("/static", __file__)

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert "/static" not in swagger_json["paths"]


def test_uri_parsed(app_with_swagger):
    @app_with_swagger.get("/<name>")
    def test(request, name):
        return text(name)

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert "/{name}" in swagger_json["paths"]


def test_ignore_options_route(app_with_swagger):
    @app_with_swagger.options("/")
    def test(request):
        return text("test")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"] == {}


def test_route_filter_all(app_with_swagger):
    app_with_swagger.config.update({"API_URI_FILTER": "all"})

    @app_with_swagger.get("/test")
    def test(request):
        return text("test")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert "/test" in swagger_json["paths"]
    assert "/test/" in swagger_json["paths"]


def test_route_filter_default(app_with_swagger):
    app_with_swagger.config.update({"API_URI_FILTER": "slash"})

    @app_with_swagger.get("/test")
    def test(request):
        return text("test")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert "/test" not in swagger_json["paths"]
    assert "/test/" in swagger_json["paths"]


def test_route_filter_slash(app_with_swagger):
    @app_with_swagger.get("/test")
    def test(request):
        return text("test")

    _, response = app_with_swagger.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert "/test" in swagger_json["paths"]
    assert "/test/" not in swagger_json["paths"]


def test_build_blueprints_route_handler_in_specs(app_with_swagger, swagger):

    bp = Blueprint("test")

    @bp.route("/")
    def test(request):
        return text("test")

    app_with_swagger.blueprint(bp)

    # only the __spec endpoint is registered on the doc
    assert len(swagger.doc._specs.keys()) == 1

    swagger.build_blueprints()

    # assert that the test route has been adding via build_blueprints
    assert len(swagger.doc._specs.keys()) == 2
    assert test in swagger.doc._specs.keys()


def test_build_blueprints_adds_name_and_tags(app_with_swagger, swagger):

    bp = Blueprint("test")

    @bp.route("/")
    def test(request):
        return text("test")

    app_with_swagger.blueprint(bp)

    swagger.build_blueprints()

    contents = swagger.doc._specs[test]

    assert contents.tags == ["test", ]
    assert contents.summary is None
    assert contents.blueprint is None
    assert contents.consumes == []
    assert contents.consumes_content_type is None
    assert contents.description is None
    assert contents.exclude is None
    assert contents.name == "test"
    assert contents.operation is None
    assert contents.produces is None
    assert contents.produces_content_type is None
    assert contents.response == []
