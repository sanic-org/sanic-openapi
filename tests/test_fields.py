from datetime import date, datetime

import pytest
from sanic.response import HTTPResponse, text

from sanic_openapi import doc


@pytest.mark.parametrize(
    "description, required, name, choices, serialized_field, path_parameters",
    [
        (None, None, None, None, {}, [{"required": True, "in": "body", "name": None}]),
        (
            "The test field",
            None,
            None,
            None,
            {"description": "The test field"},
            [
                {
                    "description": "The test field",
                    "required": True,
                    "in": "body",
                    "name": None,
                }
            ],
        ),
        (
            None,
            False,
            None,
            None,
            {"required": False},
            [
                {"required": True, "in": "body", "name": None}
            ],  # Required will be override by doc.consumes()
        ),
        (
            None,
            None,
            "test",
            None,
            {"name": "test"},
            [{"required": True, "in": "body", "name": "test"}],
        ),
        (
            None,
            None,
            None,
            ["A", "B", "C"],
            {"enum": ["A", "B", "C"]},
            [{"enum": ["A", "B", "C"], "required": True, "in": "body", "name": None}],
        ),
    ],
)
def test_base_field(
    app, description, required, name, choices, serialized_field, path_parameters
):

    field = doc.Field(
        description=description, required=required, name=name, choices=choices
    )
    assert field.serialize() == serialized_field

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"] == path_parameters


def test_integer_field(app):

    field = doc.Integer()
    assert field.serialize() == {"type": "integer", "format": "int64"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "integer",
        "format": "int64",
    }


def test_float_field(app):

    field = doc.Float()
    assert field.serialize() == {"type": "number", "format": "double"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "number",
        "format": "double",
    }


def test_string_field(app):

    field = doc.String()
    assert field.serialize() == {"type": "string"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "string",
    }


def test_boolean_field(app):

    field = doc.Boolean()
    assert field.serialize() == {"type": "boolean"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "boolean",
    }


def test_date_field(app):

    field = doc.Date()
    assert field.serialize() == {"type": "string", "format": "date"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "string",
        "format": "date",
    }


def test_datetime_field(app):

    field = doc.DateTime()
    assert field.serialize() == {"type": "string", "format": "date-time"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "string",
        "format": "date-time",
    }


def test_file_field(app):

    field = doc.File()
    assert field.serialize() == {"type": "file"}

    @app.get("/")
    @doc.consumes(field, location="formData", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "formData",
        "name": None,
        "type": "file",
    }


def test_uuid_field(app):
    field = doc.UUID(name="id")
    assert field.serialize() == {"type": "string", "format": "uuid", "name": "id"}

    @app.get("/<id:uuid>")
    @doc.consumes(field, location="path")
    @doc.response(204, {})
    def test(request):
        return HTTPResponse(status=204)

    @app.get("/")
    @doc.consumes(field, location="formData", required=True)
    @doc.response(204, {})
    def test2(request):
        return HTTPResponse(status=204)

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json

    path = swagger_json["paths"]["/{id}"]["get"]
    assert path["parameters"][0] == {
        "in": "path",
        "name": "id",
        "type": "string",
        "format": "uuid",
        "required": True,
    }

    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "in": "formData",
        "name": "id",
        "type": "string",
        "format": "uuid",
        "required": True,
    }


class TestSchema:
    pass


@pytest.mark.parametrize(
    "schema, expected_schema",
    [
        (doc.Field, {}),
        (doc.Field(), {}),
        (int, {"type": "integer", "format": "int64"}),
        (doc.Integer, {"type": "integer", "format": "int64"}),
        (doc.Integer(), {"type": "integer", "format": "int64"}),
        (float, {"type": "number", "format": "double"}),
        (doc.Float, {"type": "number", "format": "double"}),
        (doc.Float(), {"type": "number", "format": "double"}),
        (str, {"type": "string"}),
        (doc.String, {"type": "string"}),
        (doc.String(), {"type": "string"}),
        (bool, {"type": "boolean"}),
        (doc.Boolean, {"type": "boolean"}),
        (doc.Boolean(), {"type": "boolean"}),
        (date, {"type": "string", "format": "date"}),
        (doc.Date, {"type": "string", "format": "date"}),
        (doc.Date(), {"type": "string", "format": "date"}),
        (datetime, {"type": "string", "format": "date-time"}),
        (doc.DateTime, {"type": "string", "format": "date-time"}),
        (doc.DateTime(), {"type": "string", "format": "date-time"}),
        (TestSchema, {"$ref": "#/definitions/TestSchema"}),
        (dict, {"type": "object", "properties": {}}),
        ({"foo": "bar"}, {"type": "object", "properties": {"foo": {}}}),
        (list, {"type": "array", "items": []}),
        (["foo", "bar"], {"type": "array", "items": {"description": ["foo", "bar"]}}),
    ],
)
def test_serialize_schema(schema, expected_schema):
    serialized_schema = doc.serialize_schema(schema)

    assert serialized_schema == expected_schema


def test_jsonbody_field(app):
    field = doc.JsonBody()
    assert field.serialize() == {
        "name": "body",
        "schema": {"properties": {}, "type": "object"},
    }

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": "body",
        "schema": {"properties": {}, "type": "object"},
    }


@pytest.mark.parametrize(
    "field, serialized_field, path_parameters",
    [
        (
            doc.List(),
            {"type": "array", "items": []},
            {
                "required": True,
                "in": "body",
                "name": None,
                "type": "array",
                "items": [],
            },
        ),
        (
            doc.List(doc.String),
            {"type": "array", "items": {"type": "string"}},
            {
                "required": True,
                "in": "body",
                "name": None,
                "type": "array",
                "items": {"type": "string"},
            },
        ),
    ],
)
def test_list_field(app, field, serialized_field, path_parameters):
    assert field.serialize() == serialized_field

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == path_parameters


@pytest.mark.skip(reason="Failed due to global variables.")
def test_object_field(app):

    field = doc.Object(TestSchema)
    assert field.serialize() == {"type": "object", "$ref": "#/definitions/TestSchema"}

    @app.get("/")
    @doc.consumes(field, location="body", required=True)
    def test(request):
        return text("test")

    _, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
    assert response.content_type == "application/json"

    swagger_json = response.json
    path = swagger_json["paths"]["/"]["get"]
    assert path["parameters"][0] == {
        "required": True,
        "in": "body",
        "name": None,
        "type": "object",
        "schema": {"$ref": "#/definitions/TestSchema"},
    }

    assert swagger_json["definitions"]["TestSchema"] == {
        "type": "object",
        "properties": {},
    }
