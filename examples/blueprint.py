from sanic import Blueprint, Sanic
from sanic.response import json

from sanic_openapi import swagger_blueprint

app = Sanic()
app.blueprint(swagger_blueprint)

bp = Blueprint("bp", url_prefix="/bp")


@bp.route("/")
async def test(request):
    return json({"hello": "world"})


app.blueprint(bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
