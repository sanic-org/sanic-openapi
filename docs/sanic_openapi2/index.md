# Sanic OpenAPI 2

## Getting started

Here is an example to use Sanic-OpenAPI 2:

```python
from sanic import Sanic
from sanic.response import json
from sanic_openapi import openapi2_blueprint

app = Sanic("Hello world")
app.blueprint(openapi2_blueprint)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
```

And you can get your Swagger document at <http://localhost:8000/swagger> like this:
![](../_static/images/hello_world_example.png)

## Contents

* [Document Routes](/sanic_openapi2/document_routes)
* [Configurations](/sanic_openapi2/configurations)
* [Decorators](/sanic_openapi2/decorators)
* [Fields](/sanic_openapi2/fields)
* [API Factory](/sanic_openapi2/api_factory)
* [Examples](/sanic_openapi2/examples)
* [API Reference](/sanic_openapi2/api_reference)