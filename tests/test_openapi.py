from json import loads as json_loads, dumps as json_dumps
from sanic import Sanic
from sanic.response import json, text, redirect
from sanic.utils import sanic_endpoint_test
from sanic_openapi import openapi_blueprint

import pytest

# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #

def test_get_docs():
    app = Sanic('test_get')

    app.blueprint(openapi_blueprint)

    request, response = sanic_endpoint_test(app, 'get', '/openapi/spec.json')

    assert response.status == 200