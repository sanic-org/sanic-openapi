import itertools

import pytest
from sanic import Sanic

from sanic_openapi import openapi2_blueprint

app_ID = itertools.count()


@pytest.fixture()
def app():
    app = Sanic("test_{}".format(next(app_ID)))
    app.blueprint(openapi2_blueprint)
    yield app

    # Clean up
    openapi2_blueprint.definitions = {}
