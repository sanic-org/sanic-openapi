import itertools
import pytest
from sanic import Sanic

import sanic_openapi

app_ID = itertools.count()


@pytest.fixture()
def app():
    app = Sanic("test_{}".format(next(app_ID)))
    app.blueprint(sanic_openapi.swagger_blueprint)
    yield app

    # Clean up
    sanic_openapi.swagger.definitions = {}
