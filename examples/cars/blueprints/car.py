from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi import doc

from models import Car, Status


blueprint = Blueprint('Car', '/car')


@blueprint.get("/")
@doc.summary("Fetches all cars")
@doc.description("Really gets the job done fetching these cars.  I mean, really, wow.")
@doc.produces([Car])
def car_list(request):
    return json([{"car": None}])


@blueprint.get("/<car_id:int>")
@doc.summary("Fetches a car")
@doc.produces(Car)
def car_get(request, car_id):
    return json({"car": None})


@blueprint.put("/<car_id:int>")
@doc.summary("Updates a car")
@doc.consumes(Car)
@doc.produces(Car)
def car_put(request, car_id):
    return json({"car": None})


@blueprint.delete("/<car_id:int>")
@doc.summary("Deletes a car")
@doc.produces(Status)
def car_put(request, car_id):
    return json({"success": True})
