from sanic import Sanic
from sanic.response import text
from sanic.views import CompositionView

from sanic_openapi import swagger_blueprint

app = Sanic()
app.blueprint(swagger_blueprint)


def get_handler(request):
    return text("I am a get method")


view = CompositionView()
view.add(["GET"], get_handler)
view.add(["POST", "PUT"], lambda request: text("I am a post/put method"))

# Use the new view to handle requests to the base URL
app.add_route(view, "/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
