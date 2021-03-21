import datetime

from models import Car, Driver, Garage, Manufacturer, Station, Status

test_manufacturer = Manufacturer()
test_driver = Driver()
test_car = Car()
test_garage = Garage()
test_status = Status()
test_station = Station()

test_manufacturer = {
    'id': 1,
    'name': "Nissan",
    'start_date': str(datetime.date(year=1933, month=12, day=26))
}

test_driver = {
    'id': 1,
    'name': "Sanic",
    'birthday': str(datetime.date(year=2010, month=3, day=31))
}

test_car = {
    'id': 1,
    'on': False,
    'doors': 2,
    'color': 'black',
    'make': test_manufacturer,
    'passengers': [test_driver]
}

test_garage = {
    'spaces': 2,
    'cars': [test_car]
}

test_success = {
    'success': True
}

test_station = {
    'contact': 00000000,
    'location': 'Seattle',
}
