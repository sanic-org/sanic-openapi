from pathlib import Path

import yaml
from sanic_openapi import specification


def test_apply_describe(app3):
    title = "This is a test"
    version = "1.1.1"
    specification.describe(title, version=version)

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert response.json["info"]["title"] == title
    assert response.json["info"]["version"] == version


def test_raw(app3):
    with open(Path(__file__).parent / "samples" / "petstore.yaml", "r") as f:
        data = yaml.safe_load(f)

    specification.tag("one")
    specification.raw(data)
    specification.url("http://foobar")
    specification.tag("two")

    _, response = app3.test_client.get("/swagger/swagger.json")

    assert len(response.json["paths"]) == 2
    assert len(response.json["components"]["schemas"]) == 3
    assert len(response.json["servers"]) == 2
    assert len(response.json["tags"]) == 3

    assert response.json["servers"][1]["url"] == "http://foobar"
    assert {x["name"] for x in response.json["tags"]} == set(
        ["one", "two", "pets"]
    )
