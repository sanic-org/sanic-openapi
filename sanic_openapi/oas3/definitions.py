"""
Classes defined from the OpenAPI 3.0 specifications.

sanic-openapi2 equivalent  = doc.RouteField
"""
from typing import Any, Dict, List

from .types import Definition, Schema


class Reference(Schema):
    def __init__(self, value):
        super().__init__(**{"$ref": value})

    def guard(self, fields: Dict[str, Any]):
        return fields


class Example(Definition):
    summary: str
    description: str
    value: Any
    externalValue: str

    def __init__(self, value: Any = None, **kwargs):
        super().__init__(value=value, **kwargs)

    @staticmethod
    def make(value: Any, **kwargs):
        return Example(value, **kwargs)

    @staticmethod
    def external(value: Any, **kwargs):
        return Example(externalValue=value, **kwargs)


class MediaType(Definition):
    schema: Schema
    example: Any

    def __init__(self, schema: Schema, **kwargs):
        super().__init__(schema=schema, **kwargs)

    @staticmethod
    def make(value: Any):
        return MediaType(Schema.make(value))

    @staticmethod
    def all(content: Any):
        media_types = content if isinstance(content, dict) else {"*/*": content or {}}

        return {x: MediaType.make(v) for x, v in media_types.items()}


class Response(Definition):
    content: Dict[str, MediaType]
    description: str

    def __init__(self, content=None, **kwargs):
        super().__init__(content=content, **kwargs)

    @staticmethod
    def make(content, description: str = None, **kwargs):
        if not description:
            description = "Default Response"

        return Response(MediaType.all(content), description=description, **kwargs)


class RequestBody(Definition):
    description: str
    required: bool
    content: Dict[str, MediaType]

    def __init__(self, content: Dict[str, MediaType], **kwargs):
        super().__init__(content=content, **kwargs)

    @staticmethod
    def make(content: Any, **kwargs):
        return RequestBody(MediaType.all(content), **kwargs)


class ExternalDocumentation(Definition):
    url: str
    description: str

    def __init__(self, url: str, description=None):
        super().__init__(url=url, description=description)

    @staticmethod
    def make(url: str, description: str = None):
        return ExternalDocumentation(url, description)


class Header(Definition):
    name: str
    description: str
    externalDocs: ExternalDocumentation

    def __init__(self, url: str, description=None):
        super().__init__(url=url, description=description)

    @staticmethod
    def make(url: str, description: str = None):
        return Header(url, description)


class Parameter(Definition):
    name: str
    location: str
    description: str
    required: bool
    deprecated: bool
    allowEmptyValue: bool
    schema: Schema

    def __init__(self, name, schema: Schema, location="query", **kwargs):
        super().__init__(name=name, schema=schema, location=location, **kwargs)

    @property
    def fields(self):
        values = super().fields

        if 'location' in values:
            values["in"] = values.pop("location")

        return values

    @staticmethod
    def make(name: str, schema: type, location: str, **kwargs):
        if location == "path":
            kwargs["required"] = True

        return Parameter(name, Schema.make(schema), location, **kwargs)


class Operation(Definition):
    tags: List[str]
    summary: str
    description: str
    operationId: str
    requestBody: RequestBody
    externalDocs: ExternalDocumentation
    parameters: List[Parameter]
    responses: Dict[str, Response]
    security: Dict[str, List[str]]
    deprecated: bool


class PathItem(Definition):
    summary: str
    description: str
    get: Operation
    put: Operation
    post: Operation
    delete: Operation
    options: Operation
    head: Operation
    patch: Operation
    trace: Operation


class SecurityScheme(Definition):
    type: str
    description: str
    scheme: str
    bearerFormat: str
    name: str
    location: str
    openIdConnectUrl: str

    def __init__(self, type: str, **kwargs):
        super().__init__(type=type, **kwargs)

    @property
    def fields(self):
        values = super().fields

        values["in"] = values.pop("location")

        return values

    @staticmethod
    def make(_type: str, cls: type, **kwargs):
        params = cls.__dict__ if hasattr(cls, "__dict__") else {}

        return SecurityScheme(_type, **params, **kwargs)


class Tag(Definition):
    name: str
    description: str
    externalDocs: ExternalDocumentation

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)


class Components(Definition):
    schemas: Dict[str, Schema]
    responses: Dict[str, Response]
    parameters: Dict[str, Parameter]
    examples: Dict[str, Example]
    requestBodies: Dict[str, RequestBody]
    headers: Dict[str, Header]
    securitySchemes: Dict[str, SecurityScheme]
