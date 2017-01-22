from sanic import Sanic
from sanic.response import json
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc

app = Sanic()
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)


class Passenger:
    name = str
    age = int


class Car:
    doors = int
    color = str
    make = str
    passengers = [Passenger]


class Garage:
    spaces = int
    cars = [Car]


@app.get("/garage")
@doc.summary("Gets the whole garage")
@doc.produces(Garage)
async def get_garage(request):
    return json({
        "spaces": 2,
        "cars": [{"doors": 2, "make": "Nissan"}]
    })


@app.get("/garage/cars")
@doc.summary("Gets the cars in the garage")
@doc.produces({"cars": [Car]})
async def get_cars(request):
    return json({
        "cars": [{"doors": 2, "make": "Nissan"}]
    })


@app.put("/garage/car")
@doc.summary("Adds a car to the garage")
@doc.consumes(Car)
@doc.produces({"success": bool})
async def add_car(request):
    cars.append(request.json['car'])
    return json({"success": True})

app.run(debug=True)
