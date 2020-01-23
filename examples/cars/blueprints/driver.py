from sanic.blueprints import Blueprint
from sanic.response import json

from models import Driver, Status
from data import test_driver, test_success
from swagger import swagger


blueprint = Blueprint('Driver', '/driver')


@blueprint.get("/", strict_slashes=True)
@swagger.doc.summary("Fetches all drivers")
@swagger.doc.produces([Driver])
def driver_list(request):
    return json([test_driver])


@blueprint.get("/<driver_id:int>", strict_slashes=True)
@swagger.doc.summary("Fetches a driver")
@swagger.doc.produces(Driver)
def driver_get(request, driver_id):
    return json(test_driver)


@blueprint.put("/<driver_id:int>", strict_slashes=True)
@swagger.doc.summary("Updates a driver")
@swagger.doc.consumes(Driver)
@swagger.doc.produces(Driver)
def driver_put(request, driver_id):
    return json(test_driver)


@blueprint.delete("/<driver_id:int>", strict_slashes=True)
@swagger.doc.summary("Deletes a driver")
@swagger.doc.produces(Status)
def driver_delete(request, driver_id):
    return json(test_success)
