"""
   isort:skip_file
"""

from collections import defaultdict

from .builders import OperationBuilder, SpecificationBuilder

# Static datastores, which get added to via the oas3.openapi decorators,
# and then read from in the blueprint generation

operations = defaultdict(OperationBuilder)
specification = SpecificationBuilder()

from .blueprint import blueprint_factory  # noqa


openapi3_blueprint = blueprint_factory()
