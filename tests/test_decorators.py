import pytest
from sanic.response import text

from sanic_openapi import doc
from sanic_openapi.route_specs import RouteField


@pytest.mark.parametrize(
    "route_kwargs, route_fields",
    [
        ({"summary": "test"}, {"summary": "test"}),
        ({"description": "test"}, {"description": "test"}),
        ({"consumes": [RouteField(str)]}, {}),
        ({"produces": RouteField(str)}, {}),
        ({"consumes_content_type": ["text/html"]}, {"consumes": ["text/html"]}),
        ({"produces_content_type": ["text/html"]}, {"produces": ["text/html"]}),
        ({"response": [{400, RouteField(str)}]}, {}),
    ],
)
def test_route(app, swagger, route_kwargs, route_fields):
    @app.post("/")
    @swagger.doc.route(**route_kwargs)
    def test(request):
        return text("")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert all(
        item in swagger_json["paths"]["/"]["post"].items()
        for item in route_fields.items()
    )


@pytest.mark.parametrize("exclude", [True, False])
def test_exclude(app, swagger, exclude):
    @app.get("/")
    @swagger.doc.exclude(exclude)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert not ("/" in swagger_json["paths"]) == exclude


def test_summary(app, swagger):
    @app.get("/")
    @swagger.doc.summary("Test route")
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["get"]["summary"] == "Test route"


def test_description(app, swagger):
    @app.get("/")
    @swagger.doc.description("This is test route")
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["get"]["description"] == "This is test route"


class TestSchema:
    id = int


@pytest.mark.parametrize(
    "consumes_args, consumes_kwargs, parameters",
    [
        ([], {"location": "body", "required": False}, []),
        (
            [doc.String()],
            {"location": "header", "required": True, "content_type": "text/html"},
            [{"type": "string", "required": True, "in": "header", "name": None}],
        ),
        (
            [TestSchema],
            {"location": "body", "required": True, "content_type": "application/json"},
            [
                {
                    "required": True,
                    "in": "body",
                    "name": "body",
                    "schema": {"$ref": "#/definitions/TestSchema"},
                }
            ],
        ),
    ],
)
def test_consumes(app, swagger, consumes_args, consumes_kwargs, parameters):
    @app.post("/")
    @swagger.doc.consumes(*consumes_args, **consumes_kwargs)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["post"]["parameters"] == parameters


@pytest.mark.parametrize(
    "produces_args, produces_kwargs, responses",
    [
        ([], {}, {"200": {}}),
        ([doc.String], {}, {"200": {"schema": {"type": "string"}}}),
        (
            [TestSchema],
            {"content_type": "application/json"},
            {"200": {"schema": {"$ref": "#/definitions/TestSchema"}}},
        ),
    ],
)
def test_produces(app, swagger, produces_args, produces_kwargs, responses):
    @app.post("/")
    @swagger.doc.produces(*produces_args, **produces_kwargs)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["post"]["responses"] == responses


@pytest.mark.parametrize(
    "response_args, responses",
    [
        ([], {"200": {}}),
        ([201, {}], {"201": {"schema": {"type": "object", "properties": {}}}}),
    ],
)
def test_response(app, swagger, response_args, responses):
    @app.post("/")
    @swagger.doc.response(*response_args)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["post"]["responses"] == responses


def test_tag(app, swagger):
    @app.get("/")
    @swagger.doc.tag("test")
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert {"name": "test"} in swagger_json["tags"]
    assert "test" in swagger_json["paths"]["/"]["get"]["tags"]


def test_operation(app, swagger):
    @app.get("/")
    @swagger.doc.operation("This is test operation")
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    assert swagger_json["paths"]["/"]["get"]["operationId"] == "This is test operation"
