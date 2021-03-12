from sanic.blueprints import Blueprint
from sanic.response import json
from sanic.views import HTTPMethodView

from sanic_openapi import doc

blueprint = Blueprint('Class-based View', url_prefix='/class-based-view')


class MyView(HTTPMethodView):
    @doc.summary("Get my view")
    def get(self, request):
        return json({"method": "GET"})

    @doc.summary("Post my view")
    @doc.consumes({"view": {"name": str}}, location="body")
    def post(self, request):
        return json({"method": "POST"})


blueprint.add_route(MyView.as_view(), '/view', strict_slashes=True)
