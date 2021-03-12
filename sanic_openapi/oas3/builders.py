from .definitions import Any, Dict, ExternalDocumentation, List, Operation, Parameter, RequestBody, Response

"""oa2 equiv: RouteSpec """


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
    deprecated: bool = False

    def __init__(self):
        self.tags = []
        self.security = []
        self.parameters = []
        self.responses = {}

    def name(self, value: str):
        self.operationId = value

    def describe(self, summary: str = None, description: str = None):
        if summary:
            self.summary = summary

        if description:
            self.description = description

    def document(self, url: str, description: str = None):
        self.externalDocs = ExternalDocumentation(url, description)

    def tag(self, *args: str):
        for arg in args:
            self.tags.append(arg)

    def deprecate(self):
        self.deprecated = True

    def body(self, content: Any, **kwargs):
        self.requestBody = RequestBody.make(content, **kwargs)

    def parameter(self, name: str, schema: Any, location: str = "query", **kwargs):
        self.parameters.append(Parameter.make(name, schema, location, **kwargs))

    def response(self, status, content: Any = None, description: str = None, **kwargs):
        self.responses[status] = Response.make(content, description, **kwargs)

    def secured(self, *args, **kwargs):
        items = {**{v: [] for v in args}, **kwargs}
        gates = {}

        for name, params in items.items():
            gate = name.__name__ if isinstance(name, type) else name
            gates[gate] = params

        self.security.append(gates)

    def build(self):
        return Operation(**self.__dict__)
