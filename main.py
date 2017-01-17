from sanic import Sanic
from sanic.response import json
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc

app = Sanic()
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)


class Poop:
    pieces = doc.Integer()


class Butt:
    cheeks = doc.Integer()
    exports = doc.Object(Poop)


class Status:
    code = doc.Integer()
    message = doc.String()


@app.route("/test", methods=["POST"])
@doc.consumes(Butt)
@doc.produces(Status)
async def test(request):
    """
    Things and stuff
    :param request:
    :return:
    """
    return json({"test": True})

app.run(debug=True)
