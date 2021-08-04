from collections import defaultdict

from sanic.blueprints import Blueprint

from sanic_openapi import openapi, openapi3
from sanic_openapi.openapi3.blueprint import blueprint_factory
from sanic_openapi.openapi3.builders import (
    OperationBuilder,
    SpecificationBuilder,
)


def test_exclude_entire_blueprint(app3):
    _, response = app3.test_client.get("/swagger/swagger.json")
    path_count = len(response.json["paths"])
    tag_count = len(response.json["tags"])

    bp = Blueprint("noshow")

    @bp.get("/")
    def noshow(_):
        ...

    # For 21.3+
    try:
        app3.router.reset()
    except AttributeError:
        ...

    app3.blueprint(bp)
    openapi.exclude(bp=bp)

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert len(response.json["paths"]) == path_count
    assert len(response.json["tags"]) == tag_count


def test_exclude_single_blueprint_route(app3):
    _, response = app3.test_client.get("/swagger/swagger.json")
    path_count = len(response.json["paths"])
    tag_count = len(response.json["tags"])

    bp = Blueprint("somebp")

    @bp.get("/")
    @openapi.exclude()
    def noshow(_):
        ...

    @bp.get("/ok")
    def ok(_):
        ...

    # For 21.3+
    try:
        app3.router.reset()
    except AttributeError:
        ...

    app3.blueprint(bp)

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert "/ok" in response.json["paths"]
    assert len(response.json["paths"]) == path_count + 1
    assert len(response.json["tags"]) == tag_count + 1
