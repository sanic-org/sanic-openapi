from functools import partial
from typing import Any, NamedTuple, Optional

from . import doc


class Response(
    NamedTuple(
        "Response", [("code", int), ("model", Any), ("description", Optional[str])]
    )
):
    """
    HTTP status code - returned object model pair with optional description.

    If `model` is a class that has a docstring, the its docstring will be used
    as description if `description` is not set.
    """

    def __new__(cls, code: int, model: Any, description: Optional[str] = None):
        return super().__new__(cls, code, model, description)


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
        - `response`: A `Response` instance or a sequence of `Response` instances that describe
            the route's response for different HTTP status codes. The value of the `produces`
            attribute corresponds to HTTP 200, you don't have to specify that here.
        - `tag`: The tags/groups the API route belongs to.

    Example:

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
    def data(request: Request):
        return "data"
    ```

    It is possible to override all the described class attributes on a per decorator basis
    simply by passing the desired custom value to the decorator as a keyword argument:

    ```Python
    class JSONConsumerAPI(API):
        consumes_content_type = "application/json"
        consumes_location = "body"
        consumes_required = True

        class consumes:
            foo = str
            bar = str

    # The consumed data is required.
    @JSONConsumerAPI.post(app, "/data")
    def data(request: Request):
        return "data"

    # The consumed data is optional.
    @app.post("/data_optional")
    @JSONConsumerAPI(consumes_required=False)
    def data_consumed_not_required(request: Request):
        return "data"
    ```
    """

    __MISSING = "__MISSING"

    def __new__(cls, func=None, **kwargs):
        """
        Decorator that automaticaly documents the decorated route and returns the decorated method.

        Arguments:
            func: The decorated request handler function.
        """
        if func is None:
            return partial(cls, **kwargs)

        def get_attribute(obj, name, default):
            """
            Specialized attribute getter that checks every attribute name in
            `kwargs` first to allow inline overrides of attributes.

            Arguments:
                obj: The object to get the attribute value from.
                name: The name of the attribute to look up.
                default: The default value to return if the `name` attribute doesn't exist.
            """
            return kwargs[name] if name in kwargs else getattr(obj, name, default)

        # The _add_decorators() call must precede everything else.
        func = cls._add_decorators(func, get_attribute)
        func = cls._add_base_data(func, get_attribute)
        func = cls._add_consumes(func, get_attribute)
        func = cls._add_produces(func, get_attribute)
        func = cls._add_responses(func, get_attribute)
        func = cls._add_tags(func, get_attribute)
        return func

    @classmethod
    def _add_base_data(cls, func, get_attribute):
        """
        Adds basic route documentation such as summary and description.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        summary = get_attribute(cls, "summary", cls.__MISSING)
        description = get_attribute(cls, "description", cls.__MISSING)

        # If there was no explicit summary or description, determine them from
        # the class documentation if that exists.
        if summary == cls.__MISSING and description == cls.__MISSING and cls.__doc__:
            class_doc_parts = cls.__doc__.strip().split("\n\n")
            if len(class_doc_parts) > 0:
                summary = class_doc_parts[0].strip()
            if len(class_doc_parts) > 1:
                # Preserve paragraphs.
                description = "<br><br>".join(
                    part.strip() for part in class_doc_parts[1:]
                )

        return doc.route(
            summary=summary if summary != cls.__MISSING else None,
            description=description if description != cls.__MISSING else None,
            exclude=cls._exclude(get_attribute),
        )(func)

    @classmethod
    def _add_consumes(cls, func, get_attribute):
        """
        Adds the documentation of the consumed data to the route.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        value = get_attribute(cls, "consumes", None)
        # Don't register the consumed model if the route is excluded.
        if value is None or cls._exclude(get_attribute):
            return func

        # If value is a type (class), convert it to a doc.Object to be able to specify
        # its name to avoid model name conflicts and have a more readable doc.
        if isinstance(value, type):
            value = doc.Object(
                value, object_name=cls.__name__ + "Consumes", description=value.__doc__
            )

        # Use the same default values as in doc.consumes().
        return doc.consumes(
            value,
            content_type=get_attribute(cls, "consumes_content_type", None),
            location=get_attribute(cls, "consumes_location", "query"),
            required=get_attribute(cls, "consumes_required", False),
        )(func)

    @classmethod
    def _add_decorators(cls, func, get_attribute):
        """
        Adds the custom route decorators from the `decorators` class attribute to the route.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        decorators = get_attribute(cls, "decorators", None)
        if decorators is not None:
            for decorator in reversed(decorators):
                func = decorator(func)
        return func

    @classmethod
    def _add_produces(cls, func, get_attribute):
        """
        Adds the documentation of the produced data to the route.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        value = get_attribute(cls, "produces", None)
        # Don't register the produced model if the route is excluded.
        if value is None or cls._exclude(get_attribute):
            return func

        # If value is a type (class), convert it to a doc.Object to be able to specify
        # its name to avoid model name conflicts and have a more readable doc.
        if isinstance(value, type):
            produces_doc = value.__doc__.strip() if value.__doc__ else None
            produces_description = get_attribute(
                cls, "produces_description", produces_doc
            )
            value = doc.Object(
                value, object_name=cls.__name__ + "Produces", description=produces_doc
            )
        else:
            produces_description = get_attribute(cls, "produces_description", None)

        # User the same default values as in doc.produces().
        return doc.produces(
            value,
            content_type=get_attribute(cls, "produces_content_type", None),
            description=produces_description,
        )(func)

    @classmethod
    def _add_response(cls, func, response):
        """
        Adds the documentation of the behavior defined by the given `Response`
        instance to the route.

        Arguments:
            func: The decorated request handler function.
            response: The `Response` instance that defines the route's behavior.
        """
        description = response.description
        if description is None and isinstance(response.model, type):
            description = (
                response.model.__doc__.strip() if response.model.__doc__ else None
            )

        return doc.response(response.code, response.model, description=description)(
            func
        )

    @classmethod
    def _add_responses(cls, func, get_attribute):
        """
        Adds the documentation of responses corresponding to specific HTTP status
        codes to the route.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        response = get_attribute(cls, "response", None)
        if response is None:
            return func

        if isinstance(response, Response):
            return cls._add_response(func, response)

        if isinstance(response, (list, tuple)):
            for item in response:
                func = cls._add_response(func, item)

        return func

    @classmethod
    def _add_tags(cls, func, get_attribute):
        """
        Adds tags to the route.

        Arguments:
            func: The decorated request handler function.
            get_attribute: Attribute getter function to use.
        """
        value = get_attribute(cls, "tag", None)
        if isinstance(value, str):
            func = doc.tag(value)(func)
        elif isinstance(value, (list, tuple)):
            for item in value:
                func = doc.tag(item)(func)
        return func

    @classmethod
    def _exclude(cls, get_attribute):
        """
        Returns whether the route should be excluded from the documentation.

        Arguments:
            get_attribute: Attribute getter function to use.
        """
        return get_attribute(cls, "exclude", None)

    @classmethod
    def delete(cls, app, uri, **kwargs):
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
    def get(cls, app, uri, **kwargs):
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
    def head(cls, app, uri, **kwargs):
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
    def options(cls, app, uri, **kwargs):
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
    def patch(cls, app, uri, **kwargs):
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
    def post(cls, app, uri, **kwargs):
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
    def put(cls, app, uri, **kwargs):
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
    def route(cls, app, uri, *, methods, **kwargs):
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
