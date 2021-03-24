from .openapi3 import openapi3_blueprint, openapi
from .openapi2 import openapi2_blueprint, doc

swagger_blueprint = openapi2_blueprint

__version__ = "0.6.2"
__all__ = ["openapi2_blueprint", "swagger_blueprint", "openapi3_blueprint", "openapi", "doc"]
