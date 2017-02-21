from json import loads as json_loads
from sanic import Sanic
from sanic.response import json
from sanic.utils import sanic_endpoint_test
from sanic_openapi import openapi_blueprint, doc


# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #




def test_list_default():
    app = Sanic('test_get')

    app.blueprint(openapi_blueprint)

    @app.put('/test')
    @doc.consumes(doc.List(int, description="All the numbers"))
    def test(request):
        return json({"test": True})

    request, response = sanic_endpoint_test(app, 'get', '/openapi/spec.json')

    response_schema = json_loads(response.body.decode())
    parameter = response_schema['paths']['/test']['put']['parameters'][0]

    assert response.status == 200
    assert parameter['type'] == 'array'
    assert parameter['items']['type'] == 'integer'