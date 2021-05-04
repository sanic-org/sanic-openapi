import itertools
import json
from inspect import isawaitable

from sanic import Sanic
from sanic.response import HTTPResponse

from sanic_openapi import doc, openapi2_blueprint
from sanic_openapi.openapi2 import api


def test_message_api_response():
    """
    The goal here is to test whether the `json_response()` decorator is applied.
    """
    app = get_app()
    benchmark = get_benchmark_app()

    _, app_response = app.test_client.post(
        "/message", data=json.dumps({"message": "Testing"})
    )
    _, benchmark_response = benchmark.test_client.post(
        "/message", data=json.dumps({"message": "Testing"})
    )

    assert app_response.status == benchmark_response.status == 200
    assert (
        app_response.content_type
        == benchmark_response.content_type
        == "application/json"
    )
    assert app_response.headers == benchmark_response.headers
    assert (
        app_response.json == benchmark_response.json == {"message": "Message received."}
    )


def test_excluded_routes():
    """
    Tests the excluded routes that are registered using the routing methods of `API`.
    """
    app = get_app()

    # Expecting success responses.
    _, response = app.test_client.delete("/excluded_delete")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.get("/excluded_get")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.head("/excluded_head")
    assert response.status == 200
    _, response = app.test_client.options("/excluded_options")
    assert response.status == 200
    _, response = app.test_client.patch("/excluded_patch")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.post("/excluded_post")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.put("/excluded_put")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.get("/excluded_route")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}
    _, response = app.test_client.post("/excluded_route")
    assert response.status == 200
    assert response.json == {"message": "Excluded."}

    # Expecting error (these methods are not registered for the given routes).
    _, response = app.test_client.get("/excluded_delete")
    assert response.status == 405
    _, response = app.test_client.head("/excluded_get")
    assert response.status == 405
    _, response = app.test_client.options("/excluded_head")
    assert response.status == 405
    _, response = app.test_client.patch("/excluded_options")
    assert response.status == 405
    _, response = app.test_client.post("/excluded_patch")
    assert response.status == 405
    _, response = app.test_client.put("/excluded_post")
    assert response.status == 405
    _, response = app.test_client.delete("/excluded_put")
    assert response.status == 405
    _, response = app.test_client.put("/excluded_route")
    assert response.status == 405
    _, response = app.test_client.patch("/excluded_route")
    assert response.status == 405


def test_documentation():
    """
    Compares the `swagger.json` files that are returned by the app and the benchmark.
    """
    import pprint

    app = get_app()
    benchmark = get_benchmark_app()

    _, app_response = app.test_client.get("/swagger/swagger.json")
    _, benchmark_response = benchmark.test_client.get("/swagger/swagger.json")

    pprint.pprint(app_response.json)
    pprint.pprint(benchmark_response.json)

    # sanic 21.3 modifys route.name to include the app name
    # so manually check they are the same without the app name,
    # then set them to be the same.

    for path in benchmark_response.json["paths"]:
        for method in benchmark_response.json["paths"][path]:
            assert (
                app_response.json["paths"][path][method]["operationId"].split(".")[-1]
                == benchmark_response.json["paths"][path][method]["operationId"].split(
                    "."
                )[-1]
            )
            app_response.json["paths"][path][method][
                "operationId"
            ] = benchmark_response.json["paths"][path][method]["operationId"]

    assert app_response.status == benchmark_response.status == 200
    assert app_response.json == benchmark_response.json


app_ID = itertools.count()


def get_app():
    """
    Creates a Sanic application whose routes are documented using the `api` module.

    The routes and their documentation must be kept in sync with the application created
    by `get_benchmark_app()`, so that application can serve as a benchmark in test cases.
    """
    app = Sanic("test_api_{}".format(next(app_ID)))
    app.blueprint(openapi2_blueprint)

    @MessageAPI.post(app, "/message")
    def message(request):
        data = request.json
        assert "message" in data
        return {"message": "Message received."}

    @app.get("/excluded")
    @MessageAPI(exclude=True, tag="Excluded")
    def excluded(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.delete(app, "/excluded_delete")
    def excluded_delete(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.get(app, "/excluded_get")
    def excluded_get(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.head(app, "/excluded_head")
    def excluded_head(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.options(app, "/excluded_options")
    def excluded_options(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.patch(app, "/excluded_patch")
    def excluded_patch(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.post(app, "/excluded_post")
    def excluded_post(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.put(app, "/excluded_put")
    def excluded_put(request):
        return {"message": "Excluded."}

    @ExcludedMessageAPI.route(app, "/excluded_route", methods=("GET", "POST"))
    def excluded_route(request):
        return {"message": "Excluded."}

    return app


benchmark_app_ID = itertools.count()


def get_benchmark_app():
    """
    Creates a Sanic application whose routes are documented using the lower level `doc` module.

    The routes and their documentation must be kept in sync with the application created
    by `get_app()`, so this application can serve as a benchmark in test cases.
    """
    app = Sanic("test_api_benchmark_{}".format(next(benchmark_app_ID)))
    app.blueprint(openapi2_blueprint)

    @app.post("/message")
    @doc.summary("MessageAPI summary.")
    @doc.description("MessageAPI description.")
    @doc.consumes(
        doc.Object(MessageAPI.consumes, object_name="MessageAPIConsumes"),
        content_type=MessageAPI.consumes_content_type,
        location=MessageAPI.consumes_location,
        required=MessageAPI.consumes_required,
    )
    @doc.produces(
        doc.Object(MessageAPI.consumes, object_name="MessageAPIProduces"),
        content_type=MessageAPI.produces_content_type,
    )
    @doc.response(201, {"code": int})
    @doc.response(202, {"code": int}, description="202 description")
    @doc.tag("Bar")
    @doc.tag("Foo")
    @json_response
    def message(request):
        data = request.json
        assert "message" in data
        return {"message": "Message received."}

    return app


def json_response(func):
    async def inner(*args, **kwargs):
        result = func(*args, **kwargs)
        if result is None or isinstance(result, HTTPResponse):
            return result

        if isawaitable(result):
            result = await result

        return HTTPResponse(
            json.dumps(result), content_type="application/json", status=200
        )

    return inner


class JSONConsumerAPI(api.API):
    """
    Base class for API descriptor classes that consume JSON.
    """

    consumes_content_type = "application/json"
    consumes_location = "body"
    consumes_required = True


class JSONProducerAPI(api.API):
    """
    Base class for API descriptor classes that produce JSON.
    """

    decorators = (json_response,)

    produces_content_type = "application/json"


class MessageAPI(JSONConsumerAPI, JSONProducerAPI):
    """
    MessageAPI summary.

    MessageAPI description.
    """

    class consumes:
        message = str

    class produces:
        message = str

    response = (
        api.Response(201, {"code": int}),
        api.Response(202, {"code": int}, "202 description"),
    )

    tag = ("Foo", "Bar")


class ExcludedMessageAPI(MessageAPI):
    exclude = True
    tag = "Excluded"  # type: ignore
