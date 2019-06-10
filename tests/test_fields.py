from json import loads as json_loads

from sanic.response import json

from sanic_openapi import doc

# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #


def test_list_default(app):

    @app.put("/test")
    @doc.consumes(doc.List(int, description="All the numbers"), location="body")
    def test(request):
        return json({"test": True})

    _, response = app.test_client.get("/swagger/swagger.json")

    response_schema = json_loads(response.body.decode())
    parameter = response_schema["paths"]["/test"]["put"]["parameters"][0]

    assert response.status == 200
    assert parameter["type"] == "array"
    assert parameter["items"]["type"] == "integer"