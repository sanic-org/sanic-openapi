from sanic.blueprints import Blueprint
from sanic.response import json

from models import Car, Status
from data import test_car, test_success
from swagger import swagger


blueprint = Blueprint('Car', '/car')


@blueprint.get("/", strict_slashes=True)
@swagger.doc.summary("Fetches all cars")
@swagger.doc.description(
    "Really gets the job done fetching these cars.  I mean, really, wow."
)
@swagger.doc.produces([Car])
def car_list(request):
    return json([test_car])


@blueprint.get("/<car_id:int>", strict_slashes=True)
@swagger.doc.summary("Fetches a car")
@swagger.doc.produces(Car)
def car_get(request, car_id):
    return json(test_car)


@blueprint.put("/<car_id:int>", strict_slashes=True)
@swagger.doc.summary("Updates a car")
@swagger.doc.consumes(Car, location='body')
@swagger.doc.consumes({'AUTHORIZATION': str}, location='header')
@swagger.doc.produces(Car)
def car_put(request, car_id):
    return json(test_car)


@blueprint.delete("/<car_id:int>", strict_slashes=True)
@swagger.doc.summary("Deletes a car")
@swagger.doc.produces(Status)
def car_delete(request, car_id):
    return json(test_success)
