# Sanic OpenAPI

[![Build Status](https://travis-ci.org/channelcat/sanic-openapi.svg?branch=master)](https://travis-ci.org/channelcat/sanic-openapi)
[![PyPI](https://img.shields.io/pypi/v/sanic-openapi.svg)](https://pypi.python.org/pypi/sanic-openapi/)
[![PyPI](https://img.shields.io/pypi/pyversions/sanic-openapi.svg)](https://pypi.python.org/pypi/sanic-openapi/)

Give your Sanic API a UI and OpenAPI documentation, all for the price of free!

![Example Swagger UI](images/code-to-ui.png?raw=true "Swagger UI")

## Installation

```shell
pip install sanic-openapi
```

Add OpenAPI and Swagger UI:

```python
from sanic_openapi import swagger_blueprint, openapi_blueprint

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
```

You'll now have a Swagger UI at the URL `/swagger`.  
Your routes will be automatically categorized by their blueprints.

## Example

For an example Swagger UI, see the [Pet Store](http://petstore.swagger.io/)

## Usage

### Use simple decorators to document routes:

```python
from sanic_openapi import doc

@app.get("/user/<user_id:int>")
@doc.summary("Fetches a user by ID")
@doc.produces({ "user": { "name": str, "id": int } })
async def get_user(request, user_id):
    ...

@app.post("/user")
@doc.summary("Creates a user")
@doc.consumes({"user": { "name": str }}, location="body")
async def create_user(request):
    ...
```

### Model your input/output

```python
class Car:
    make = str
    model = str
    year = int

class Garage:
    spaces = int
    cars = [Car]

@app.get("/garage")
@doc.summary("Gets the whole garage")
@doc.produces(Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"make": "Nissan", "model": "370Z"}]
    })

```

### Get more descriptive

```python
class Car:
    make = doc.String("Who made the car")
    model = doc.String("Type of car.  This will vary by make")
    year = doc.Integer("4-digit year of the car", required=False)

class Garage:
    spaces = doc.Integer("How many cars can fit in the garage")
    cars = doc.List(Car, description="All cars in the garage")
```

### Configure all the things

```python
app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Car API'
app.config.API_DESCRIPTION = 'Car API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_PRODUCES_CONTENT_TYPES = ['application/json']
app.config.API_CONTACT_EMAIL = 'channelcat@gmail.com'
```

### Additional documentation strings

A new response decorator will allow you to add a series of responses
supporting a status code, description and optional example.

```python
@doc.response('200', 'Successful Operation', {'handle': '1195ff38-d2e2-11e7-8edb-bcaec5447bf4'})
@doc.response('404', 'File not found')
@doc.response('500', 'Application erroor')
```
