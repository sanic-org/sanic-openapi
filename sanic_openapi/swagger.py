from .oas3.blueprint import blueprint_factory as oas3_factory
from .swagger2.blueprint import blueprint_factory as swagger_factory

swagger_blueprint = swagger_factory()
oas3_blueprint = oas3_factory()
