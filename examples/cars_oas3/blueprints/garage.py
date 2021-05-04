import json

from sanic.blueprints import Blueprint
from sanic.response import json

from data import test_garage, test_success
from models import Car, Garage, Status
from sanic_openapi import openapi

blueprint = Blueprint('Garage', '/garage')


@blueprint.get("/", strict_slashes=True)
@openapi.summary("Fetches the garage")
@openapi.response(200, {"application/json" : Garage})
async def get_garage(request):
    return json(test_garage)


@blueprint.get("/cars", strict_slashes=True)
@openapi.summary("Fetches the cars in the garage")
@openapi.body(
    { "application/json" : {"doors": int} },
    description="Body description",
    required=True,
)
@openapi.response(200, {"application/json" : {"cars": [Car]}})
async def get_cars(request):
    return json(test_garage.get('cars'))


@blueprint.put("/car", strict_slashes=True)
@openapi.summary("Adds a car to the garage")
@openapi.body(
    { "application/json" : Car },
    description="Body description",
    required=True,
)
@openapi.response(204, {"application/json" : Status})
async def add_car(request):
    return json(test_success)
