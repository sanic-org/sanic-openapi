"""
This module provides decorators which append
documentation to operations and components created in the blueprints.

"""
from typing import Any

from . import operations
from .types import (  # noqa
    Array,
    Binary,
    Boolean,
    Byte,
    Date,
    DateTime,
    Double,
    Email,
    Float,
    Integer,
    Long,
    Object,
    Password,
    String,
    Time,
)


def operation(name: str):
    def inner(func):
        operations[func].name(name)
        return func

    return inner


def summary(text: str):
    def inner(func):
        operations[func].describe(summary=text)
        return func

    return inner


def description(text: str):
    def inner(func):
        operations[func].describe(description=text)
        return func

    return inner


def document(url: str, description: str = None):
    def inner(func):
        operations[func].document(url, description)
        return func

    return inner


def tag(*args: str):
    def inner(func):
        operations[func].tag(*args)
        return func

    return inner


def deprecated():
    def inner(func):
        operations[func].deprecate()
        return func

    return inner


def body(content: Any, **kwargs):
    def inner(func):
        operations[func].body(content, **kwargs)
        return func

    return inner


def parameter(name: str, schema: Any, location: str = "query", **kwargs):
    def inner(func):
        operations[func].parameter(name, schema, location, **kwargs)
        return func

    return inner


def response(status, content: Any = None, description: str = None, **kwargs):
    def inner(func):
        operations[func].response(status, content, description, **kwargs)
        return func

    return inner


def secured(*args, **kwargs):
    raise NotImplementedError(
        "SecuritySchemas are not yet implemented in sanic-openapi 0.6.3, "
        "hopefully they should be ready for the next release."
    )

    def inner(func):
        operations[func].secured(*args, **kwargs)
        return func

    return inner
