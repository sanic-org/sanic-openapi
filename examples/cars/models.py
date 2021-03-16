from datetime import date

from sanic_openapi import doc


class Manufacturer:
    name = str
    start_date = date


class Driver:
    name: str
    birthday: date


class Car:
    on = bool
    doors = int
    color = str
    make = Manufacturer
    driver = Driver
    passengers = [Driver]


class Garage:
    spaces = int
    cars = [Car]


class Status:
    success = bool


class Station:
    location = doc.String("location")
    contact = doc.Integer("phone number")
