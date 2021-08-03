from sanic.blueprints import Blueprint
from sanic_openapi import openapi


def test_exclude_entire_blueprint(app3):
    bp = Blueprint("noshow")

    @bp.get("/")
    def noshow(_):
        ...

    app3.blueprint(bp)
    openapi.exclude(bp=bp)

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert not response.json["paths"]
    assert not response.json["tags"]


def test_exclude_single_blueprint_route(app3):
    bp = Blueprint("noshow")

    @bp.get("/")
    @openapi.exclude()
    def noshow(_):
        ...

    @bp.get("/ok")
    def ok(_):
        ...

    app3.blueprint(bp)

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert "/ok" in response.json["paths"]
    assert len(response.json["paths"]) == 1
    assert len(response.json["tags"]) == 1
