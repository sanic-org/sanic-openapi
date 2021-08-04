"""
   isort:skip_file
"""

from collections import defaultdict
from typing import Dict, TypeVar
from .builders import OperationBuilder, SpecificationBuilder

try:
    from sanic.models.handler_types import RouteHandler
except ImportError:
    RouteHandler = TypeVar("RouteHandler")  # type: ignore

# Static datastores, which get added to via the oas3.openapi decorators,
# and then read from in the blueprint generation

operations: Dict[RouteHandler, OperationBuilder] = defaultdict(
    OperationBuilder
)
specification = SpecificationBuilder()


from .blueprint import blueprint_factory  # noqa


openapi3_blueprint = blueprint_factory()
