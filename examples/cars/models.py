from datetime import date


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
    passengers = [Driver]


class Garage:
    spaces = int
    cars = [Car]


class Status:
    success = bool
