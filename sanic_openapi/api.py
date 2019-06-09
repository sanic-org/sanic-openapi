from typing import Callable, Sequence

from sanic_openapi import doc


class API:
    """
    Decorator factory class for documenting routes using `sanic_openapi` and optionally
    registering them in a `sanic` application or blueprint.

    Supported class attribute names match the corresponding `sanic_openapi.doc` decorator's
    name and attribute values work exactly as if they were passed to the given decorator
    unless explicitly documented otherwise. The supported class attributes (all of which
    are optional) are as follows:
        - `summary`: Its value should be the short summary of the route. If neither `summary`
            nor `description` is specified, then the first paragraph of the API class'
            documentation will be used instead. You may also set it to `None` to disable
            automatic `summary` and `description` generation.
        - `description`: A longer description of the route. If neither `summary` nor
            `description` is specified, then the API class' documentation will be used
            except its first paragraph that serves as the default summary. You may also
            set it to `None` to disable automatic `summary` and `description` generation.
        - `exclude`: Whether to exclude the route (and related models) from the API documentation.
        - `consumes`: The model of the data the API route consumes. If `consumes` is a class
            that has a docstring, then the docstring will be used as the description of th data.
        - `consumes_content_type`: The content type of the data the API route consumes.
        - `consumes_location`: The location where the data is expected (`query` or `body`).
        - `consumes_required`: Whether the consumed data is required.
        - `produces`: The model of the data the API route produces.
        - `produces_content_type`: The content type of the data the API route produces.
        - `produces_description`: The description of the data the API route produces. If
            not specified but `produces` is a class that has a docstring, then the docstring
            will be used as the default description.
        - `tag`: The tags/groups the API route belongs to.

    Additionally, you may specify a `decorators` class attribute, whose value must be a
    sequence of decorators to apply on the decorated routes. These decorators will be
    applied *before* the `sanic_openapi` decorators - and the `sanic` routing decorators
    if the routing decorators provided by this class are used - in *reverse* order. It
    means that the following cases are equivalent:

    ```Python
    class Data(API):
        class consumes:
            stg = str

    class DecoratedData(Data):
        decorators = (first, second)

    @DecoratedData.get(app, "/data")
    def data_all_in_one(request: Request):
        return "data"

    @app.get("/data")
    @DecoratedData
    def data_doc_and_decorators_in_one(request: Request):
        return "data"

    @Data.get(app, "/data")
    @first
    @second
    def data_routing_and_doc_in_one(request: Request):
        return "data"

    @app.get("/data")
    @Data
    @first
    @second
    def data(request:Request):
        return "data"
    ```

    Example usage this class:

    ```Python
    class JSONConsumerAPI(API):
        consumes_content_type = "application/json"
        consumes_location = "body"
        consumes_required = True

    class JSONProducerAPI(API):
        produces_content_type = "application/json"

    class MyAPI(JSONConsumerAPI, JSONProducerAPI):
        \"\"\"
        Route *summary* in first paragraph.

        First paragraph of route *description*.

        Second paragraph of route *description*.
        \"\"\"

        class consumes:
            foo = str
            bar = str

        class produces:
            result = bool

    # Document and register the route at once.
    @MyAPI.post(app, "/my_route")
    def my_route(request: Request):
        return {"result": True}

    # Or simply document a route.
    @app.post("/my_route")
    @MyAPI
    def my_route(request: Request):
        return {"result": True}
    ```
    """

    __MISSING: str = "__MISSING"

    def __new__(cls, func: Callable) -> Callable:
        """
        Decorator that automaticaly documents the decorated route and returns the decorated method.

        Arguments:
            func: The decorated request handler function.
        """
        # ----- Additional decorators

        decorators = getattr(cls, "decorators", None)
        if decorators is not None:
            for decorator in reversed(decorators):
                func = decorator(func)

        # ----- Process summary, description and exclude.

        summary = getattr(cls, "summary", cls.__MISSING)
        description = getattr(cls, "description", cls.__MISSING)
        exclude = getattr(cls, "exclude", None)

        # If there was no explicit summary or description, determine them from
        # the class documentation if that exists.
        if summary == cls.__MISSING and description == cls.__MISSING and cls.__doc__:
            class_doc_parts = cls.__doc__.strip().split("\n\n")
            if len(class_doc_parts) > 0:
                summary = class_doc_parts[0].strip()
            if len(class_doc_parts) > 1:
                # Preserve paragraphs.
                description = "<br><br>".join(part.strip() for part in class_doc_parts[1:])

        doc.route(
            summary=summary if summary != cls.__MISSING else None,
            description=description if description != cls.__MISSING else None,
            exclude=exclude
        )(func)

        # ----- Process consumes attributes.

        value = getattr(cls, "consumes", None)
        if value is not None and not exclude:
            # If value is a type (class), convert it to a doc.Object to be able to specify
            # its name to avoid model name conflicts and have a more readable doc.
            if isinstance(value, type):
                value = doc.Object(value, object_name=cls.__name__+"Consumes", description=value.__doc__)

            # Use the same default values as in doc.consumes().
            doc.consumes(
                value,
                content_type=getattr(cls, "consumes_content_type", None),
                location=getattr(cls, "consumes_location", "query"),
                required=getattr(cls, "consumes_required", False)
            )(func)

        # ----- Process produces attributes.

        value = getattr(cls, "produces", None)
        if value is not None and not exclude:
            # If value is a type (class), convert it to a doc.Object to be able to specify
            # its name to avoid model name conflicts and have a more readable doc.
            if isinstance(value, type):
                produces_doc = value.__doc__.strip() if value.__doc__ else None
                produces_description = getattr(cls, "produces_description", produces_doc)
                value = doc.Object(value, object_name=cls.__name__+"Produces", description=produces_doc)
            else:
                produces_description = getattr(cls, "produces_description", None)

            # User the same default values as in doc.produces().
            doc.produces(
                value,
                content_type=getattr(cls, "produces_content_type", None),
                description=produces_description
            )(func)

        # ----- Process tags.

        value = getattr(cls, "tag", None)
        if isinstance(value, str):
            doc.tag(value)(func)
        elif isinstance(value, (list, tuple)):
            for item in value:
                doc.tag(item)(func)

        return func

    @classmethod
    def delete(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `DELETE` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `delete()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.delete(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def get(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `GET` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `get()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.get(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def head(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `HEAD` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `head()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.head(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def options(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `OPTIONS` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `options()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.options(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def patch(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `PATCH` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `patch()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.patch(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def post(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `POST` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `post()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.post(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def put(cls, app, uri: str, **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        The decorated method will be registered for `PUT` requests.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `put()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.put(uri, **kwargs)(cls(func))
        return inner

    @classmethod
    def route(cls, app, uri: str, *, methods: Sequence[str], **kwargs):
        """
        Decorator that registers the decorated route in the given `sanic` application or
        blueprint with the given URI, and also documents its API using `sanic_openapi`.

        Keyword arguments that are not listed in arguments section will be passed on to the
        `sanic` application's or blueprint's `route()` method as they are.

        Arguments:
            app: The `sanic` application or blueprint where the route should be registered.
            uri: The URI the route should be accessible at.
        """
        def inner(func):
            return app.route(uri, methods=methods, **kwargs)(cls(func))
        return inner
