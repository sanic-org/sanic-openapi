from .builders import ComponentsBuilder, OperationsBuilder, SpecificationBuilder

#
# Static datastores for spec.
#
components = ComponentsBuilder()
operations = OperationsBuilder()
specification = SpecificationBuilder(components)
