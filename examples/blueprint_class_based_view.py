from sanic import Blueprint, Sanic
from sanic.response import text
from sanic.views import HTTPMethodView

from sanic_openapi import swagger_blueprint

app = Sanic()
app.blueprint(swagger_blueprint)

bp = Blueprint("bp", url_prefix="/bp")


class SimpleView(HTTPMethodView):
    def get(self, request):
        return text("I am get method")

    def post(self, request):
        return text("I am post method")

    def put(self, request):
        return text("I am put method")

    def patch(self, request):
        return text("I am patch method")

    def delete(self, request):
        return text("I am delete method")

    def options(self, request):  # This will not be documented.
        return text("I am options method")


bp.add_route(SimpleView.as_view(), "/")
app.blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
