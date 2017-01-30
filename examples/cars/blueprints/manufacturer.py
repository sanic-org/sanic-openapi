from sanic.blueprints import Blueprint
from sanic.response import json
from sanic_openapi import doc

from models import Driver, Status


blueprint = Blueprint('Manufacturer', '/manufacturer')


@blueprint.get("/")
@doc.summary("Fetches all manufacturers")
@doc.produces([Driver])
def manufacturer_list(request):
    return json([{"manufacturer": None}])


@blueprint.get("/<manufacturer_id:int>")
@doc.summary("Fetches a manufacturer")
@doc.produces(Driver)
def manufacturer_get(request, manufacturer_id):
    return json({"manufacturer": None})


@blueprint.put("/<manufacturer_id:int>")
@doc.summary("Updates a manufacturer")
@doc.consumes(Driver)
@doc.produces(Driver)
def manufacturer_put(request, manufacturer_id):
    return json({"manufacturer": None})


@blueprint.delete("/<manufacturer_id:int>")
@doc.summary("Deletes a manufacturer")
@doc.produces(Status)
def manufacturer_delete(request, manufacturer_id):
    return json({"success": True})
