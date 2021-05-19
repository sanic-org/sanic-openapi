from .openapi2 import doc, openapi2_blueprint
from .openapi3 import openapi, openapi3_blueprint

swagger_blueprint = openapi2_blueprint

__version__ = "21.3.2"
__all__ = [
    "openapi2_blueprint",
    "swagger_blueprint",
    "openapi3_blueprint",
    "openapi",
    "doc",
]
