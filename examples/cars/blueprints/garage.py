from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi import doc

from models import Garage, Car, Status
from data import test_garage, test_success
import json


blueprint = Blueprint('Garage', '/garage')


@blueprint.get("/", strict_slashes=True)
@doc.summary("Fetches the garage")
@doc.produces(Garage)
async def get_garage(request):
    return json(test_garage)


@blueprint.get("/cars", strict_slashes=True)
@doc.summary("Fetches the cars in the garage")
@doc.consumes({"doors": int})
@doc.produces({"cars": [Car]})
async def get_cars(request):
    return json(test_garage.get('cars'))


@blueprint.put("/car", strict_slashes=True)
@doc.summary("Adds a car to the garage")
@doc.consumes(Car)
@doc.produces(Status)
async def add_car(request):
    return json(test_success)
