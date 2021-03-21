from datetime import date

from sanic_openapi import openapi


class Manufacturer:
    name = str
    start_date = date


class Driver:
    name = str
    birthday = date


class Car:
    on = bool
    doors = int
    color = str
    make = Manufacturer
    driver = Driver
    passengers = openapi.Array(Driver, required=["name", "birthday"])


class Garage:
    spaces = int
    cars = [Car]


class Status:
    success = bool


class Station:
    location = openapi.String(description="location")
    contact = openapi.Integer(description="phone number")
