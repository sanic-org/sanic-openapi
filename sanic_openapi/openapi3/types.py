import json
import typing as t
from datetime import date, datetime, time
from enum import Enum
from inspect import isclass
from typing import Any, Dict, List, Union, get_type_hints


class Definition:
    __fields: dict

    def __init__(self, **kwargs):
        self.__fields = self.guard(kwargs)

    @property
    def fields(self):
        return self.__fields

    def guard(self, fields):
        return {
            k: v
            for k, v in fields.items()
            if k in _properties(self).keys() or k.startswith("x-")
        }

    def serialize(self):
        return _serialize(self.fields)

    def __str__(self):
        return json.dumps(self.serialize())

    def apply(self, func, operations, *args, **kwargs):
        op = operations[func]
        method_name = getattr(
            self.__class__, "__method__", self.__class__.__name__.lower()
        )
        method = getattr(op, method_name)
        if not args and not kwargs:
            kwargs = self.__dict__
        method(*args, **kwargs)


class Schema(Definition):
    title: str
    description: str
    type: str
    format: str
    nullable: bool
    required: bool
    default: None
    example: None
    oneOf: List[Definition]
    anyOf: List[Definition]
    allOf: List[Definition]

    multipleOf: int
    maximum: int
    exclusiveMaximum: bool
    minimum: int
    exclusiveMinimum: bool
    maxLength: int
    minLength: int
    pattern: str
    enum: Union[List[Any], Enum]

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
            return Object.make(value, **kwargs)
        elif _type == t._GenericAlias and value.__origin__ == list:
            return Array(Schema.make(value.__args__[0]), **kwargs)
        else:
            return Object.make(value, **kwargs)


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

    @classmethod
    def make(cls, value: Any, **kwargs):
        return cls(
            {k: Schema.make(v) for k, v in _properties(value).items()},
            **kwargs,
        )


class Array(Schema):
    items: Any
    maxItems: int
    minItems: int
    uniqueItems: bool

    def __init__(self, items: Any, **kwargs):
        super().__init__(type="array", items=Schema.make(items), **kwargs)


def _serialize(value) -> Any:
    if isinstance(value, Definition):
        return value.serialize()

    if isinstance(value, type) and issubclass(value, Enum):
        return [item.value for item in value.__members__.values()]

    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}

    if isinstance(value, list):
        return [_serialize(v) for v in value]

    return value


def _properties(value: object) -> Dict:
    try:
        fields = {x: v for x, v in value.__dict__.items()}
    except AttributeError:
        fields = {}

    cls = value if isclass(value) else value.__class__
    return {
        k: v
        for k, v in {**get_type_hints(cls), **fields}.items()
        if not k.startswith("_")
    }
