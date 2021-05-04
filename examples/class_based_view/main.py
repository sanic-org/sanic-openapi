from sanic import Sanic
from sanic.response import json

from blueprint import blueprint
from sanic_openapi import doc, swagger_blueprint

app = Sanic("Class Based View example")

app.blueprint(swagger_blueprint)
app.blueprint(blueprint)


@app.post("/plain", strict_slashes=True)
@doc.summary("Creates a user")
@doc.consumes({"user": {"name": str}}, location="body")
async def create_user(request):
    return json({})


app.config.API_VERSION = 'pre-alpha'
app.config.API_TITLE = 'Class Based View Demonstration API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_CONTACT_EMAIL = 'guoli-lyu@hotmail.com'

app.run(host="0.0.0.0", debug=True)
