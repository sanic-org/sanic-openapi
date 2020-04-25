import collections.abc
import uuid
from datetime import date, datetime
from itertools import chain
from typing import Dict, Optional, get_type_hints


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

        register_as = object_name or "{}".format(cls.__qualname__)
        if register_as not in self.definitions:
            self.definitions[register_as] = self.definition

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
