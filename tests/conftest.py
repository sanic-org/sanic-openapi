import pytest
from sanic import Sanic
from sanic_openapi import swagger_blueprint


@pytest.fixture()
def app():
    app = Sanic('test')
    app.blueprint(swagger_blueprint)
    return app
