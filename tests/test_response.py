from json import loads as json_loads
from sanic import Sanic
from sanic.response import json
from sanic_openapi import openapi_blueprint, doc


def test_responses():
    app = Sanic('test_responses')

    app.blueprint(openapi_blueprint)

    @app.put('/test', strict_slashes=True)
    @doc.responses(201, 'Created')
    @doc.responses(404, 'Not found')
    def test(request):
        return json({"test": True})

    request, response = app.test_client.get('/openapi/spec.json')

    response_schema = json_loads(response.body.decode())

    responses = response_schema['paths']['/test']['put']['responses']

    assert str(201) in responses
    assert str(404) in responses

test_responses()