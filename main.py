from sanic import Sanic
from sanic.response import json
from sanic_openapi import blueprint

app = Sanic()
app.blueprint(blueprint)


class Butt:
    """
    :prop pet: Your Pet
    """
    pet: str

    def test(self):
        return None


@app.route("/test")
async def test(request):
    """
    Things and stuff
    :consumes: multipart/form-data Butt
    :produces: application/json
    :param request:
    :return:
    """
    return json({"test": True})

app.run(debug=True)
