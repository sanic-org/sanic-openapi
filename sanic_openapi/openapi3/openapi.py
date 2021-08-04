"""
This module provides decorators which append
documentation to operations and components created in the blueprints.

"""
from typing import Any, Dict, List, Optional, Sequence, Union

from sanic.blueprints import Blueprint
from sanic.exceptions import SanicException

from sanic_openapi.openapi3.definitions import (
    ExternalDocumentation,
    Parameter,
    RequestBody,
    Response,
    Tag,
)

from . import operations
from .types import Array  # noqa
from .types import Binary  # noqa
from .types import Boolean  # noqa
from .types import Byte  # noqa
from .types import Date  # noqa
from .types import DateTime  # noqa
from .types import Double  # noqa
from .types import Email  # noqa
from .types import Float  # noqa
from .types import Integer  # noqa
from .types import Long  # noqa
from .types import Object  # noqa
from .types import Password  # noqa
from .types import String  # noqa
from .types import Time  # noqa


def exclude(flag: bool = True, *, bp: Optional[Blueprint] = None):
    if bp:
        for route in bp.routes:
            exclude(flag)(route.handler)
        return

    def inner(func):
        operations[func].exclude(flag)
        return func

    return inner


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


def definition(
    *,
    exclude: Optional[bool] = None,
    operation: Optional[str] = None,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    document: Optional[Union[str, ExternalDocumentation]] = None,
    tag: Optional[Union[Union[str, Tag], Sequence[Union[str, Tag]]]] = None,
    deprecated: bool = False,
    body: Optional[Union[Dict[str, Any], RequestBody, Any]] = None,
    parameter: Optional[
        Union[
            Union[Dict[str, Any], Parameter, str],
            List[Union[Dict[str, Any], Parameter, str]],
        ]
    ] = None,
    response: Optional[
        Union[
            Union[Dict[str, Any], Response, Any],
            List[Union[Dict[str, Any], Response, Any]],
        ]
    ] = None,
):
    def inner(func):
        glbl = globals()

        if exclude is not None:
            glbl["exclude"](exclude)(func)

        if operation:
            glbl["operation"](operation)(func)

        if summary:
            glbl["summary"](summary)(func)

        if description:
            glbl["description"](description)(func)

        if document:
            kwargs = {}
            if isinstance(document, str):
                kwargs["url"] = document
            else:
                kwargs["url"] = document.fields["url"]
                kwargs["description"] = document.fields["description"]

            glbl["document"](**kwargs)(func)

        if tag:
            taglist = []
            op = (
                "extend"
                if isinstance(tag, (list, tuple, set, frozenset))
                else "append"
            )

            getattr(taglist, op)(tag)
            glbl["tag"](
                *[
                    tag.fields["name"] if isinstance(tag, Tag) else tag
                    for tag in taglist
                ]
            )(func)

        if deprecated:
            glbl["deprecated"]()(func)

        if body:
            kwargs = {}
            if isinstance(body, RequestBody):
                kwargs = body.fields
            elif isinstance(body, dict):
                if "content" in body:
                    kwargs = body
                else:
                    kwargs["content"] = body
            else:
                kwargs["content"] = body
            glbl["body"](**kwargs)(func)

        if parameter:
            paramlist = []
            op = (
                "extend"
                if isinstance(parameter, (list, tuple, set, frozenset))
                else "append"
            )
            getattr(paramlist, op)(parameter)

            for param in paramlist:
                kwargs = {}
                if isinstance(param, Parameter):
                    kwargs = param.fields
                elif isinstance(param, dict) and "name" in param:
                    kwargs = param
                elif isinstance(param, str):
                    kwargs["name"] = param
                else:
                    raise SanicException(
                        "parameter must be a Parameter instance, a string, or "
                        "a dictionary containing at least 'name'."
                    )

                if "schema" not in kwargs:
                    kwargs["schema"] = str

                glbl["parameter"](**kwargs)(func)

        if response:
            resplist = []
            op = (
                "extend"
                if isinstance(response, (list, tuple, set, frozenset))
                else "append"
            )
            getattr(resplist, op)(response)

            for resp in resplist:
                kwargs = {}
                if isinstance(resp, Response):
                    kwargs = resp.fields
                elif isinstance(resp, dict):
                    if "content" in resp:
                        kwargs = resp
                    else:
                        kwargs["content"] = resp
                else:
                    kwargs["content"] = resp

                if "status" not in kwargs:
                    kwargs["status"] = 200

                glbl["response"](**kwargs)(func)

        return func

    return inner
