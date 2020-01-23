from sanic.blueprints import Blueprint
from sanic.response import json

from models import Garage, Car, Status
from data import test_garage, test_success
from swagger import swagger


blueprint = Blueprint('Garage', '/garage')


@blueprint.get("/", strict_slashes=True)
@swagger.doc.summary("Fetches the garage")
@swagger.doc.produces(Garage)
async def get_garage(request):
    return json(test_garage)


@blueprint.get("/cars", strict_slashes=True)
@swagger.doc.summary("Fetches the cars in the garage")
@swagger.doc.consumes({"doors": int})
@swagger.doc.produces({"cars": [Car]})
async def get_cars(request):
    return json(test_garage.get('cars'))


@blueprint.put("/car", strict_slashes=True)
@swagger.doc.summary("Adds a car to the garage")
@swagger.doc.consumes(Car)
@swagger.doc.produces(Status)
async def add_car(request):
    return json(test_success)
