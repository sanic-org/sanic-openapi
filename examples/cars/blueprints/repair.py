from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import HTTPMethodView

from app import swagger
from data import test_station
from models import Station

blueprint = Blueprint('Repair', '/repair')


class RepairStation(HTTPMethodView):
    @swagger.doc.summary("Fetches all repair stations")
    @swagger.doc.produces([Station])
    def get(self, request):
        return json([test_station])

    @swagger.doc.summary("make an appointment")
    @swagger.doc.description("submit necessary information for appointment")
    def post(self, request):
        return json(request.json)


blueprint.add_route(RepairStation.as_view(), "/station", strict_slashes=True)
