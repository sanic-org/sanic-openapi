import pytest

from sanic_openapi import openapi
from sanic_openapi.openapi3.definitions import (
    ExternalDocumentation,
    Parameter,
    RequestBody,
    Response,
    Tag,
)
from sanic_openapi.openapi3.types import Schema, _serialize


class Name:
    first_name: str
    last_name: str


class User:
    name: Name


def test_def_operation(app3):
    @app3.post("/path")
    @openapi.definition(
        operation="operID",
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    op = response.json["paths"]["/path"]["post"]

    assert op["operationId"] == "operID"


def test_def_summary(app3):
    @app3.post("/path")
    @openapi.definition(
        summary="Hello, world.",
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    op = response.json["paths"]["/path"]["post"]

    assert op["summary"] == "Hello, world."


def test_def_description(app3):
    @app3.post("/path")
    @openapi.definition(
        description="Hello, world.",
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    op = response.json["paths"]["/path"]["post"]

    assert op["description"] == "Hello, world."


@pytest.mark.parametrize(
    "value",
    (
        "foo",
        Tag("foo"),
        ["foo"],
        [Tag("foo")],
        [Tag("foo"), "bar"],
    ),
)
def test_def_tag(app3, value):
    @app3.post("/path")
    @openapi.definition(
        tag=value,
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    op = response.json["paths"]["/path"]["post"]
    length = len(value) if isinstance(value, list) else 1

    assert "foo" in op["tags"]
    assert len(op["tags"]) == length


@pytest.mark.parametrize(
    "value",
    ("http://somewhere", ExternalDocumentation("http://somewhere")),
)
def test_def_document(app3, value):
    @app3.post("/path")
    @openapi.definition(
        document=value,
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    op = response.json["paths"]["/path"]["post"]

    assert op["externalDocs"]["url"] == "http://somewhere"


@pytest.mark.parametrize(
    "media,value",
    (
        ("*/*", User),
        ("*/*", {"*/*": User}),
        ("*/*", {"content": {"*/*": User}}),
        ("*/*", RequestBody(User)),
        ("*/*", RequestBody(content=User)),
        ("application/json", RequestBody({"application/json": User})),
    ),
)
def test_def_body(app3, media, value):
    @app3.post("/path")
    @openapi.definition(
        body=value,
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    body = response.json["paths"]["/path"]["post"]["requestBody"]

    assert body["content"][media]["schema"] == _serialize(Schema.make(User))


@pytest.mark.parametrize(
    "type_,value",
    (
        ("string", "something"),
        ("string", {"name": "something"}),
        ("string", ["something", "else"]),
        ("integer", {"name": "something", "schema": int}),
        ("string", Parameter("something", str)),
        ("string", [Parameter("something", str)]),
    ),
)
def test_def_parameter(app3, value, type_):
    @app3.post("/path")
    @openapi.definition(
        parameter=value,
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    params = response.json["paths"]["/path"]["post"]["parameters"]

    length = len(value) if isinstance(value, list) else 1

    assert len(params) == length
    assert params[0]["name"] == "something"
    assert params[0]["schema"]["type"] == type_


@pytest.mark.parametrize(
    "status,media,value",
    (
        (200, "*/*", User),
        (200, "application/json", {"application/json": User}),
        (200, "*/*", Response(User)),
        (201, "*/*", Response(User, 201)),
        (201, "*/*", [Response(User, 201), User]),
        (200, "application/json", Response({"application/json": User})),
    ),
)
def test_def_response(app3, status, media, value):
    @app3.post("/path")
    @openapi.definition(
        response=value,
    )
    async def handler(request):
        ...

    _, response = app3.test_client.get("/swagger/swagger.json")
    responses = response.json["paths"]["/path"]["post"]["responses"]

    length = len(value) if isinstance(value, list) else 1

    assert len(responses) == length
    assert responses[f"{status}"]["content"][media] == {
        "schema": _serialize(Schema.make(User))
    }
