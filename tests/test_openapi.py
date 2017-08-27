from sanic import Sanic
from sanic_openapi import openapi_blueprint

# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #

def test_get_docs():
    app = Sanic('test_get')
    app.blueprint(openapi_blueprint)
    
    request, response = app.test_client.get('/openapi/spec.json')
    assert response.status == 200
