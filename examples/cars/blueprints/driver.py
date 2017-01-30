from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi import doc

from models import Driver, Status


blueprint = Blueprint('Driver', '/driver')


@blueprint.get("/")
@doc.summary("Fetches all drivers")
@doc.produces([Driver])
def driver_list(request):
    return json([{"driver": None}])


@blueprint.get("/<driver_id:int>")
@doc.summary("Fetches a driver")
@doc.produces(Driver)
def driver_get(request, driver_id):
    return json({"driver": None})


@blueprint.put("/<driver_id:int>")
@doc.summary("Updates a driver")
@doc.consumes(Driver)
@doc.produces(Driver)
def driver_put(request, driver_id):
    return json({"driver": None})


@blueprint.delete("/<driver_id:int>")
@doc.summary("Deletes a driver")
@doc.produces(Status)
def driver_delete(request, driver_id):
    return json({"success": True})
