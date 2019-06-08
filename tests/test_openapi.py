from sanic import Sanic
from sanic_openapi import swagger_blueprint

# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #


def test_get_docs():
    app = Sanic("test_get")
    app.blueprint(swagger_blueprint)

    request, response = app.test_client.get("/swagger/swagger.json")
    assert response.status == 200
