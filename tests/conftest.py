import pytest
from sanic import Sanic

from sanic_openapi.swagger import Swagger


@pytest.fixture
def app():
    app = Sanic("test")
    yield app


@pytest.fixture
def swagger(app):
    _swagger = Swagger(app)
    yield _swagger


@pytest.fixture
def app_with_swagger(app, swagger):
    yield app
