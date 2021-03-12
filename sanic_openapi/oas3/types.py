"""
Classes defined from the OpenAPI 3.0 specifications.

sanic-openapi2 equivalent  = doc.String, etc
"""
import json
from datetime import date, datetime, time
from typing import Any, Dict, List, get_type_hints


def _serialize(value) -> Any:
    if isinstance(value, Definition):
        return value.serialize()

    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_serialize(v) for v in value]

    return value


def _properties(value: object) -> Dict:
    fields = {k: v for k, v in value.__dict__.items() if not k.startswith("_")}

    return {**get_type_hints(value.__class__), **fields}


class Definition:
    fields: dict

    def __init__(self, **kwargs):
        self.fields = self.guard(kwargs)

    def guard(self, fields):
        return {k: v for k, v in fields.items() if k in _properties(self).keys() or k.startswith("x-")}

    def serialize(self):
        return _serialize(self.fields)

    def __str__(self):
        return json.dumps(self.serialize())


class Schema(Definition):
    title: str
    description: str
    type: str
    format: str
    nullable: False
    required: False
    default: None
    example: None
    oneOf: List[Definition]
    anyOf: List[Definition]
    allOf: List[Definition]

    multipleOf: int
    maximum: int
    exclusiveMaximum: False
    minimum: int
    exclusiveMinimum: False
    maxLength: int
    minLength: int
    pattern: str

    @staticmethod
    def make(value, **kwargs):
        if isinstance(value, Schema):
            return value

        if value == bool:
            return Boolean(**kwargs)
        elif value == int:
            return Integer(**kwargs)
        elif value == float:
            return Float(**kwargs)
        elif value == str:
            return String(**kwargs)
        elif value == bytes:
            return Byte(**kwargs)
        elif value == bytearray:
            return Binary(**kwargs)
        elif value == date:
            return Date(**kwargs)
        elif value == time:
            return Time(**kwargs)
        elif value == datetime:
            return DateTime(**kwargs)

        _type = type(value)

        if _type == bool:
            return Boolean(default=value, **kwargs)
        elif _type == int:
            return Integer(default=value, **kwargs)
        elif _type == float:
            return Float(default=value, **kwargs)
        elif _type == str:
            return String(default=value, **kwargs)
        elif _type == bytes:
            return Byte(default=value, **kwargs)
        elif _type == bytearray:
            return Binary(default=value, **kwargs)
        elif _type == date:
            return Date(**kwargs)
        elif _type == time:
            return Time(**kwargs)
        elif _type == datetime:
            return DateTime(**kwargs)
        elif _type == list:
            if len(value) == 0:
                schema = Schema(nullable=True)
            elif len(value) == 1:
                schema = Schema.make(value[0])
            else:
                schema = Schema(oneOf=[Schema.make(x) for x in value])

            return Array(schema, **kwargs)
        elif _type == dict:
            return Object({k: Schema.make(v) for k, v in value.items()}, **kwargs)
        else:
            return Object({k: Schema.make(v) for k, v in _properties(value).items()}, **kwargs)


class Boolean(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="boolean", **kwargs)


class Integer(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int32", **kwargs)


class Long(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="integer", format="int64", **kwargs)


class Float(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="float", **kwargs)


class Double(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="number", format="double", **kwargs)


class String(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", **kwargs)


class Byte(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="byte", **kwargs)


class Binary(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="binary", **kwargs)


class Date(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date", **kwargs)


class Time(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="time", **kwargs)


class DateTime(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="date-time", **kwargs)


class Password(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="password", **kwargs)


class Email(Schema):
    def __init__(self, **kwargs):
        super().__init__(type="string", format="email", **kwargs)


class Object(Schema):
    properties: Dict[str, Schema]
    maxProperties: int
    minProperties: int

    def __init__(self, properties: Dict[str, Schema] = None, **kwargs):
        super().__init__(type="object", properties=properties or {}, **kwargs)


class Array(Schema):
    items: Schema
    maxItems: int
    minItems: int
    uniqueItems: False

    def __init__(self, items: Schema, **kwargs):
        super().__init__(type="array", items=items, **kwargs)
