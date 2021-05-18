"""
Builders for the oas3 object types

These are completely internal, so can be refactored if desired without concern
for breaking user experience
"""
from collections import defaultdict

from ..autodoc import YamlStyleParametersParser
from ..utils import remove_nulls, remove_nulls_from_kwargs
from .definitions import (
    Any,
    Contact,
    Dict,
    ExternalDocumentation,
    Info,
    License,
    List,
    OpenAPI,
    Operation,
    Parameter,
    PathItem,
    RequestBody,
    Response,
    Server,
    Tag,
)


class OperationBuilder:
    summary: str
    description: str
    operationId: str
    requestBody: RequestBody
    externalDocs: ExternalDocumentation
    tags: List[str]
    security: List[Any]
    parameters: List[Parameter]
    responses: Dict[str, Response]
    callbacks: List[str]  # TODO
    deprecated: bool = False

    def __init__(self):
        self.tags = []
        self.security = []
        self.parameters = []
        self.responses = {}
        self._autodoc = None

    def name(self, value: str):
        self.operationId = value

    def describe(self, summary: str = None, description: str = None):
        if summary:
            self.summary = summary

        if description:
            self.description = description

    def document(self, url: str, description: str = None):
        self.externalDocs = ExternalDocumentation.make(url, description)

    def tag(self, *args: str):
        for arg in args:
            self.tags.append(arg)

    def deprecate(self):
        self.deprecated = True

    def body(self, content: Any, **kwargs):
        self.requestBody = RequestBody.make(content, **kwargs)

    def parameter(
        self, name: str, schema: Any, location: str = "query", **kwargs
    ):
        self.parameters.append(
            Parameter.make(name, schema, location, **kwargs)
        )

    def response(
        self, status, content: Any = None, description: str = None, **kwargs
    ):
        self.responses[status] = Response.make(content, description, **kwargs)

    def secured(self, *args, **kwargs):
        items = {**{v: [] for v in args}, **kwargs}
        gates = {}

        for name, params in items.items():
            gate = name.__name__ if isinstance(name, type) else name
            gates[gate] = params

        self.security.append(gates)

    def build(self):
        operation_dict = self.__dict__.copy()
        if not self.responses:
            # todo -- look into more consistent default response format
            operation_dict["responses"]["default"] = {"description": "OK"}

        if self._autodoc:
            operation_dict.update(self._autodoc)

        return Operation(**operation_dict)

    def autodoc(self, docstring: str):
        y = YamlStyleParametersParser(docstring)
        self._autodoc = y.to_openAPI_3()


class SpecificationBuilder:
    _urls: List[str]
    _title: str
    _version: str
    _description: str
    _terms: str
    _contact: Contact
    _license: License
    _paths: Dict[str, Dict[str, OperationBuilder]]
    _tags: Dict[str, Tag]
    # _components: ComponentsBuilder
    # deliberately not included

    def __init__(self):
        self._paths = defaultdict(dict)
        self._tags = {}
        self._license = None
        self._urls = []

    def url(self, value: str):
        self._urls.append(value)

    def describe(
        self,
        title: str,
        version: str,
        description: str = None,
        terms: str = None,
    ):
        self._title = title
        self._version = version
        self._description = description
        self._terms = terms

    def tag(self, name: str, **kwargs):
        self._tags[name] = Tag(name, **kwargs)

    def contact(self, name: str = None, url: str = None, email: str = None):
        kwargs = remove_nulls_from_kwargs(name=name, url=url, email=email)
        self._contact = Contact(**kwargs)

    def license(self, name: str = None, url: str = None):
        if name is not None:
            self._license = License(name, url=url)

    def operation(self, path: str, method: str, operation: OperationBuilder):
        for _tag in operation.tags:
            if _tag in self._tags.keys():
                continue

            self._tags[_tag] = Tag(_tag)

        self._paths[path][method.lower()] = operation

    def build(self) -> OpenAPI:
        info = self._build_info()
        paths = self._build_paths()
        tags = self._build_tags()

        url_servers = getattr(self, "_urls", None)
        servers = []
        if url_servers is not None:
            for url_server in url_servers:
                servers.append(Server(url=url_server))

        return OpenAPI(info, paths, tags=tags, servers=servers)

    def _build_info(self) -> Info:
        kwargs = remove_nulls(
            {
                "description": self._description,
                "termsOfService": self._terms,
                "license": self._license,
                "contact": self._contact,
            },
            deep=False,
        )

        return Info(self._title, self._version, **kwargs)

    def _build_tags(self):
        return [self._tags[k] for k in self._tags]

    def _build_paths(self) -> Dict:
        paths = {}

        for path, operations in self._paths.items():
            paths[path] = PathItem(
                **{k: v.build() for k, v in operations.items()}
            )

        return paths
