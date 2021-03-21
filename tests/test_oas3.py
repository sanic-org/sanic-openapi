import itertools
import json
from inspect import isawaitable

from sanic import Sanic
from sanic.response import HTTPResponse, json as json_response

from sanic_openapi import api, openapi, oas3_blueprint

from sanic_openapi.oas3 import openapi


def test_documentation():
    """
    Check the `swagger.json` file.
    """
    app = get_app()

    _, app_response = app.test_client.get("/swagger/swagger.json")
    post_operation = app_response.json["paths"]["/garage"]["post"]
    body_props = post_operation["requestBody"]["content"]["application/json"]["schema"]["properties"]
    assert post_operation["description"] == "Create a new garage"
    car_schema_in_body = body_props["cars"]
    assert car_schema_in_body["required"] == False
    assert car_schema_in_body["type"] == "array"
    assert len(car_schema_in_body["items"]["properties"]) == 3
    spaces_schema_in_body = body_props["spaces"]
    assert spaces_schema_in_body["required"] == True
    assert spaces_schema_in_body["format"] == "int32"
    assert spaces_schema_in_body["type"] == "integer"
    assert spaces_schema_in_body["description"] == "Space available in the garage"
    assert app_response.status == 200


app_ID = itertools.count()


def get_app():
    """
    Creates a Sanic application whose routes are documented using the `openPI` module.
    """
    app = Sanic("test_api_oas3_{}".format(next(app_ID)))
    app.blueprint(oas3_blueprint)


    class Car:
        manufacturer = openapi.String(description="Car manufacturer", required=True)
        model = openapi.String(description="Car model", required=True)
        production_date = openapi.Date(description="Car year", required=True)


    class Garage:
        spaces = openapi.Integer(description="Space available in the garage", required=True)
        cars = openapi.Array(Car, required=False)


    @app.post('/garage')
    @openapi.description("Create a new garage")
    @openapi.body(
        { "application/json" : Garage },
        description="Body description",
        location="/garage",
        required=True,
    )
    @openapi.response(
        201, { "application/json" : Garage }, "A new Garage has been created"
    )
    async def create_garage(request):
        return json_response(request.json, 201)

    return app
