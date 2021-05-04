import json

from sanic.blueprints import Blueprint
from sanic.response import json

from data import test_driver, test_success
from models import Driver, Status
from sanic_openapi import openapi

blueprint = Blueprint('Driver', '/driver')


@blueprint.get("/", strict_slashes=True)
@openapi.summary("Fetches all drivers")
@openapi.response(200, {"application/json" : [Driver]})
def driver_list(request):
    return json([test_driver])


@blueprint.get("/<driver_id:int>", strict_slashes=True)
@openapi.summary("Fetches a driver")
@openapi.response(200, {"application/json" : Driver})
def driver_get(request, driver_id):
    return json(test_driver)


@blueprint.put("/<driver_id:int>", strict_slashes=True)
@openapi.summary("Updates a driver")
@openapi.body(
    { "application/json" : Driver },
    description="Body description",
    required=True,
)
@openapi.response(200, {"application/json" : Driver})
def driver_put(request, driver_id):
    return json(test_driver)


@blueprint.delete("/<driver_id:int>", strict_slashes=True)
@openapi.summary("Deletes a driver")
@openapi.response(204, {"application/json" : Status})
def driver_delete(request, driver_id):
    return json(test_success)
