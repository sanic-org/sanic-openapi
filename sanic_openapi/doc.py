import collections.abc
import uuid
from collections import defaultdict
from datetime import date, datetime
from itertools import chain
from typing import Dict, Optional, get_type_hints

from .spec import Spec


class Field:
    def __init__(self, description=None, required=None, name=None, choices=None):
        self.name = name
        self.description = description
        self.required = required
        self.choices = choices

    def serialize(self):
        output = {}
        if self.name:
            output["name"] = self.name
        if self.description:
            output["description"] = self.description
        if self.required is not None:
            output["required"] = self.required
        if self.choices is not None:
            output["enum"] = self.choices
        return output


class Integer(Field):
    def serialize(self):
        return {"type": "integer", "format": "int64", **super().serialize()}


class Float(Field):
    def serialize(self):
        return {"type": "number", "format": "double", **super().serialize()}


class String(Field):
    def serialize(self):
        return {"type": "string", **super().serialize()}


class Boolean(Field):
    def serialize(self):
        return {"type": "boolean", **super().serialize()}


class Tuple(Field):
    pass


class Date(Field):
    def serialize(self):
        return {"type": "string", "format": "date", **super().serialize()}


class DateTime(Field):
    def serialize(self):
        return {"type": "string", "format": "date-time", **super().serialize()}


class File(Field):
    def serialize(self):
        return {"type": "file", **super().serialize()}


class Dictionary(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs)

    def serialize(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema) for key, schema in self.fields.items()
            },
            **super().serialize(),
        }


class JsonBody(Field):
    def __init__(self, fields=None, **kwargs):
        self.fields = fields or {}
        super().__init__(**kwargs, name="body")

    def serialize(self):
        return {
            "schema": {
                "type": "object",
                "properties": {
                    key: serialize_schema(schema) for key, schema in self.fields.items()
                },
            },
            **super().serialize(),
        }


class List(Field):
    def __init__(self, items=None, *args, **kwargs):
        self.items = items or []
        if type(self.items) is not list:
            self.items = [self.items]
        super().__init__(*args, **kwargs)

    def serialize(self):
        if len(self.items) > 1:
            items = Tuple(self.items).serialize()
        elif self.items:
            items = serialize_schema(self.items[0])
        else:
            items = []
        return {"type": "array", "items": items, **super().serialize()}


class UUID(Field):
    def serialize(self):
        return {"type": "string", "format": "uuid", **super().serialize()}


class Object(Field):
    def __init__(
        self, cls, *args, definitions: Optional[Dict] = None, object_name=None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.cls = cls
        self.object_name = object_name or cls.__name__
        self.definitions = definitions or {}

        register_as = object_name or "{}.{}".format(cls.__module__, cls.__qualname__)
        if register_as not in self.definitions:
            self.definitions[register_as] = (self, self.definition)

    @property
    def definition(self):
        return {
            "type": "object",
            "properties": {
                key: serialize_schema(schema)
                for key, schema in chain(
                    self.cls.__dict__.items(), get_type_hints(self.cls).items()
                )
                if not key.startswith("_")
            },
            **super().serialize(),
        }

    def serialize(self):
        return {
            "type": "object",
            "$ref": "#/definitions/{}".format(self.object_name),
            **super().serialize(),
        }


def serialize_class(schema):
    if issubclass(schema, Field):
        return schema().serialize()
    elif schema is dict:
        return Dictionary().serialize()
    elif schema is list:
        return List().serialize()
    elif schema is int:
        return Integer().serialize()
    elif schema is float:
        return Float().serialize()
    elif schema is str:
        return String().serialize()
    elif schema is bool:
        return Boolean().serialize()
    elif schema is date:
        return Date().serialize()
    elif schema is datetime:
        return DateTime().serialize()
    elif schema is uuid.UUID:
        return UUID().serialize()
    else:
        return Object(schema).serialize()


def serialize_schema(schema):
    schema_type = type(schema)

    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if issubclass(schema_type, type):
        return serialize_class(schema)

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, Field):
            return schema.serialize()
        elif schema_type is dict:
            return Dictionary(schema).serialize()
        elif schema_type is list:
            return List(schema).serialize()
        elif getattr(schema, "__origin__", None) in (list, collections.abc.Sequence):
            # Type hinting with either List or Sequence
            return List(list(schema.__args__)).serialize()

    return {}


# --------------------------------------------------------------- #
# Route Documenters
# --------------------------------------------------------------- #


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
    def __init__(self):
        self._specs = defaultdict(RouteSpec)

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
            return func

        return inner

    def produces(self, *args, description=None, content_type=None):
        def inner(func):
            if args:
                routefield = RouteField(args[0], description=description)
                self._specs[func].produces = routefield
                self._specs[func].produces_content_type = [content_type]
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
