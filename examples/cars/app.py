from sanic import Sanic
from sanic_openapi import Swagger


app = Sanic()
swagger = Swagger(app)
