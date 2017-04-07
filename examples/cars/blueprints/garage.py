from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi import doc

from models import Garage, Car, Status


blueprint = Blueprint('Garage', '/garage')


@blueprint.get("/")
@doc.summary("Fetches the garage")
@doc.produces(Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"doors": 2, "make": "Nissan"}]
    })


@blueprint.get("/cars")
@doc.summary("Fetches the cars in the garage")
@doc.consumes({"doors": int})
@doc.produces({"cars": [Car]})
async def get_cars(request):
    return json({
        "cars": [{"doors": 2, "make": "Nissan"}]
    })


@blueprint.put("/car")
@doc.summary("Adds a car to the garage")
@doc.consumes(Car)
@doc.produces(Status)
async def add_car(request):
    return json({"success": True})
