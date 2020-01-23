from sanic.blueprints import Blueprint
from sanic.response import json

from models import Driver, Status
from data import test_manufacturer, test_success
from swagger import swagger


blueprint = Blueprint('Manufacturer', '/manufacturer')


@blueprint.get("/", strict_slashes=True)
@swagger.doc.summary("Fetches all manufacturers")
@swagger.doc.produces([Driver])
def manufacturer_list(request):
    return json([test_manufacturer])


@blueprint.get("/<manufacturer_id:int>", strict_slashes=True)
@swagger.doc.summary("Fetches a manufacturer")
@swagger.doc.produces(Driver)
def manufacturer_get(request, manufacturer_id):
    return json(test_manufacturer)


@blueprint.put("/<manufacturer_id:int>", strict_slashes=True)
@swagger.doc.summary("Updates a manufacturer")
@swagger.doc.consumes(Driver)
@swagger.doc.produces(Driver)
def manufacturer_put(request, manufacturer_id):
    return json(test_manufacturer)


@blueprint.delete("/<manufacturer_id:int>", strict_slashes=True)
@swagger.doc.summary("Deletes a manufacturer")
@swagger.doc.produces(Status)
def manufacturer_delete(request, manufacturer_id):
    return json(test_success)
