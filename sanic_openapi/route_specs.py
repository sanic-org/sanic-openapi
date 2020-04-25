from collections import defaultdict

from sanic_openapi.spec import Spec


class RouteSpec(object):
    consumes = None
    consumes_content_type = None
    produces = None
    produces_content_type = None
    summary = None
    description = None
    operation = None
    tags = None
    exclude = None
    response = None
    blueprint = None
    name = None

    def __init__(self):
        self.tags = []
        self.consumes = []
        self.response = []
        super().__init__()


class RouteField(object):
    field = None
    location = None
    required = None
    description = None

    def __init__(self, field, location=None, required=False, description=None):
        self.field = field
        self.location = location
        self.required = required
        self.description = description


class RouteSpecs:
    def __init__(self, spec: Spec):
        self._specs = defaultdict(RouteSpec)
        self.spec = spec

    def get(self, key):
        return self._specs[key]

    @property
    def specs(self):
        return {k: v for k, v in self._specs.items() if not v.exclude}

    def values(self):
        return self.specs.values()

    def route(
        self,
        summary=None,
        description=None,
        consumes=None,
        produces=None,
        consumes_content_type=None,
        produces_content_type=None,
        exclude=None,
        response=None,
    ):
        def inner(func):
            route_spec = self._specs[func]

            if summary is not None:
                route_spec.summary = summary
            if description is not None:
                route_spec.description = description
            if consumes is not None:
                route_spec.consumes = consumes
            if produces is not None:
                route_spec.produces = produces
            if consumes_content_type is not None:
                route_spec.consumes_content_type = consumes_content_type
            if produces_content_type is not None:
                route_spec.produces_content_type = produces_content_type
            if exclude is not None:
                route_spec.exclude = exclude
            if response is not None:
                route_spec.response = response

            return func

        return inner

    def exclude(self, boolean):
        def inner(func):
            self._specs[func].exclude = boolean
            return func

        return inner

    def summary(self, text):
        def inner(func):
            self._specs[func].summary = text
            return func

        return inner

    def description(self, text):
        def inner(func):
            self._specs[func].description = text
            return func

        return inner

    def consumes(self, *args, content_type=None, location="query", required=False):
        def inner(func):
            if args:
                for arg in args:
                    field = RouteField(arg, location, required)
                    self._specs[func].consumes.append(field)
                    self._specs[func].consumes_content_type = [content_type]
                    self.spec.add_definitions(arg)
            return func

        return inner

    def produces(self, *args, description=None, content_type=None):
        def inner(func):
            if args:
                routefield = RouteField(args[0], description=description)
                self._specs[func].produces = routefield
                self._specs[func].produces_content_type = [content_type]
                self.spec.add_definitions(args[0])
            return func

        return inner

    def response(self, *args, description=None):
        def inner(func):
            if args:
                status_code = args[0]
                routefield = RouteField(args[1], description=description)
                self._specs[func].response.append((status_code, routefield))
            return func

        return inner

    def tag(self, name):
        def inner(func):
            self._specs[func].tags.append(name)
            return func

        return inner

    def operation(self, name):
        def inner(func):
            self._specs[func].operation = name
            return func

        return inner
