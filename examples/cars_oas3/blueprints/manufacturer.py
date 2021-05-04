from sanic.blueprints import Blueprint
from sanic.response import json

from data import test_manufacturer, test_success
from models import Driver, Status
from sanic_openapi import openapi

blueprint = Blueprint('Manufacturer', '/manufacturer')


@blueprint.get("/", strict_slashes=True)
@openapi.summary("Fetches all manufacturers")
@openapi.response(200, {"application/json" : [Driver]})
def manufacturer_list(request):
    return json([test_manufacturer])


@blueprint.get("/<manufacturer_id:int>", strict_slashes=True)
@openapi.summary("Fetches a manufacturer")
@openapi.response(200, {"application/json" : Driver})
def manufacturer_get(request, manufacturer_id):
    return json(test_manufacturer)


@blueprint.put("/<manufacturer_id:int>", strict_slashes=True)
@openapi.summary("Updates a manufacturer")
@openapi.body(
    { "application/json" : Driver },
    description="Body description",
    required=True,
)
@openapi.response(200, {"application/json" : Driver})
def manufacturer_put(request, manufacturer_id):
    return json(test_manufacturer)


@blueprint.delete("/<manufacturer_id:int>", strict_slashes=True)
@openapi.summary("Deletes a manufacturer")
@openapi.response(200, {"application/json" : Status})
def manufacturer_delete(request, manufacturer_id):
    return json(test_success)
