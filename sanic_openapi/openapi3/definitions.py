"""
Classes defined from the OpenAPI 3.0 specifications.

I.e., the objects described https://swagger.io/docs/specification

"""
from typing import Any, Dict, List, Optional, Type, Union

from .types import Definition, Schema


class Reference(Schema):
    def __init__(self, value):
        super().__init__(**{"$ref": value})

    def guard(self, fields: Dict[str, Any]):
        return fields


class Contact(Definition):
    name: str
    url: str
    email: str


class License(Definition):
    name: str
    url: str

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)


class Info(Definition):
    title: str
    description: str
    termsOfService: str
    contact: Contact
    license: License
    version: str

    def __init__(self, title: str, version: str, **kwargs):
        super().__init__(title=title, version=version, **kwargs)


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
        media_types = (
            content if isinstance(content, dict) else {"*/*": content or {}}
        )

        return {x: MediaType.make(v) for x, v in media_types.items()}


class Response(Definition):
    content: Union[Any, Dict[str, Union[Any, MediaType]]]
    description: Optional[str]
    status: str

    def __init__(
        self,
        content: Optional[Union[Any, Dict[str, Union[Any, MediaType]]]] = None,
        status: int = 200,
        description: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            content=content, status=status, description=description, **kwargs
        )

    @staticmethod
    def make(content, description: str = None, **kwargs):
        if not description:
            description = "Default Response"

        return Response(
            MediaType.all(content), description=description, **kwargs
        )


class RequestBody(Definition):
    description: Optional[str]
    required: Optional[bool]
    content: Union[Any, Dict[str, Union[Any, MediaType]]]

    def __init__(
        self,
        content: Union[Any, Dict[str, Union[Any, MediaType]]],
        required: Optional[bool] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Can be initialized with content in one of a few ways:

        RequestBody(SomeModel)
        RequestBody({"application/json": SomeModel})
        RequestBody({"application/json": {"name": str}})
        """
        super().__init__(
            content=content,
            required=required,
            description=description,
            **kwargs,
        )

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
    schema: Union[Type, Schema]
    location: str
    description: Optional[str]
    required: Optional[bool]
    deprecated: Optional[bool]
    allowEmptyValue: Optional[bool]

    def __init__(
        self,
        name: str,
        schema: Union[Type, Schema],
        location: str = "query",
        description: Optional[str] = None,
        required: Optional[bool] = None,
        deprecated: Optional[bool] = None,
        allowEmptyValue: Optional[bool] = None,
        **kwargs,
    ):
        super().__init__(
            name=name,
            schema=schema,
            location=location,
            description=description,
            required=required,
            deprecated=deprecated,
            allowEmptyValue=allowEmptyValue,
            **kwargs,
        )

    @property
    def fields(self):
        values = super().fields

        if "location" in values:
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
    callbacks: List[str]  # TODO
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

        if "location" in values:
            values["in"] = values.pop("location")

        return values

    @staticmethod
    def make(_type: str, cls: Type, **kwargs):
        params = cls.__dict__ if hasattr(cls, "__dict__") else {}

        return SecurityScheme(_type, **params, **kwargs)


class ServerVariable(Definition):
    default: str
    description: str
    enum: List[str]

    def __init__(self, default: str, **kwargs):
        super().__init__(default=default, **kwargs)


class Server(Definition):
    url: str
    description: str
    variables: Dict[str, ServerVariable]

    def __init__(
        self, url: str, description: str = None, variables: dict = None
    ):
        super().__init__(
            url=url, description=description, variables=variables or []
        )


class Tag(Definition):
    name: str
    description: str
    externalDocs: ExternalDocumentation

    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)


class Components(Definition):
    # This class is not being used in sanic-openapi right now, but the
    # definition is kept here to keep in close accordance with the openapi
    # spec, in case it is desired to be added later.
    schemas: Dict[str, Schema]
    responses: Dict[str, Response]
    parameters: Dict[str, Parameter]
    examples: Dict[str, Example]
    requestBodies: Dict[str, RequestBody]
    headers: Dict[str, Header]
    securitySchemes: Dict[str, SecurityScheme]
    links: Dict[str, Schema]  # TODO
    callbacks: Dict[str, Schema]  # TODO


class OpenAPI(Definition):
    openapi: str
    info: Info
    servers: List[Server]
    paths: Dict[str, PathItem]
    components: Components
    security: Dict[str, SecurityScheme]
    tags: List[Tag]
    externalDocs: ExternalDocumentation

    def __init__(self, info: Info, paths: Dict[str, PathItem], **kwargs):
        super().__init__(openapi="3.0.0", info=info, paths=paths, **kwargs)
