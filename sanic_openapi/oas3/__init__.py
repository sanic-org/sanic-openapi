from collections import defaultdict

from .builders import OperationBuilder

# Static datastore for spec.

operations = defaultdict(OperationBuilder)
