from sanic.blueprints import Blueprint
from sanic.response import json

from data import test_car, test_success
from models import Car, Status
from sanic_openapi import openapi

blueprint = Blueprint('Car', '/car')


@blueprint.get("/", strict_slashes=True)
@openapi.summary("Fetches all cars")
@openapi.description("Really gets the job done fetching these cars.  I mean, really, wow.")
@openapi.response(200, {"application/json" : [Car]})
def car_list(request):
    return json([test_car])


@blueprint.get("/<car_id:int>", strict_slashes=True)
@openapi.summary("Fetches a car")
@openapi.response(200, {"application/json" : Car})
def car_get(request, car_id):
    return json(test_car)


@blueprint.put("/<car_id:int>", strict_slashes=True)
@openapi.summary("Updates a car")
@openapi.body(
    { "application/json" : Car },
    description="Body description",
    required=True,
)
@openapi.parameter("AUTHORIZATION", str, location="header")
@openapi.response(200, {"application/json" : Car})
def car_put(request, car_id):
    return json(test_car)


@blueprint.delete("/<car_id:int>", strict_slashes=True)
@openapi.summary("Deletes a car")
@openapi.response(204, {"application/json" : Status})
def car_delete(request, car_id):
    return json(test_success)
