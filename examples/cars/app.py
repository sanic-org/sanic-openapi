from sanic import Sanic
from sanic_openapi.swagger import Swagger


app = Sanic()
swagger = Swagger(app)
