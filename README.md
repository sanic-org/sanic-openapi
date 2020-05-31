# Sanic OpenAPI

[![Build Status](https://travis-ci.org/huge-success/sanic-openapi.svg?branch=master)](https://travis-ci.org/huge-success/sanic-openapi)
[![PyPI](https://img.shields.io/pypi/v/sanic-openapi.svg)](https://pypi.python.org/pypi/sanic-openapi/)
[![PyPI](https://img.shields.io/pypi/pyversions/sanic-openapi.svg)](https://pypi.python.org/pypi/sanic-openapi/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![codecov](https://codecov.io/gh/huge-success/sanic-openapi/branch/master/graph/badge.svg)](https://codecov.io/gh/huge-success/sanic-openapi)

Give your Sanic API a UI and OpenAPI documentation, all for the price of free!

![Example Swagger UI](docs/_static/images/code-to-ui.png?raw=true "Swagger UI")

## Installation

```shell
pip install sanic-openapi
```

Add Swagger UI with the OpenAPI spec:

```python
from sanic_openapi import Swagger

Swagger(app)
```

You'll now have a Swagger UI at the URL `/swagger/` and an OpenAPI 2.0 spec at `/swagger/swagger.json`.
Your routes will be automatically categorized by their blueprints.

## Example

Here is an example to use Sanic-OpenAPI:
```python
from sanic import Sanic
from sanic.response import json
from sanic_openapi import Swagger

app = Sanic()
Swagger(app)


@app.route("/")
async def test(request):
    return json({"hello": "world"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

```

And you can get your Swagger document at <http://localhost:8000/swagger> like this:
![](docs/_static/images/hello_world_example.png)

## Documentation

Please check the documentation on [Readthedocs](https://sanic-openapi.readthedocs.io)

## Contribution

Any contribution is welcome. If you don't know how to getting started, please check issues first and check our [Contributing Guide](CONTRIBUTING.md) to start you contribution.
