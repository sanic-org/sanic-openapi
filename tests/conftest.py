import pytest
from sanic import Sanic

from sanic_openapi.swagger import Swagger


@pytest.fixture()
def app():
    app = Sanic("test")
    swagger = Swagger()
    swagger.init_app(app)
    yield app
