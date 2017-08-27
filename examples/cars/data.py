from models import Car, Driver, Garage, Manufacturer, Status
import datetime

test_manufacturer = Manufacturer()
test_driver = Driver()
test_car = Car()
test_garage = Garage()
test_status = Status()

test_manufacturer = {
    'id': 1,
    'name': "Nissan",
    'start_date': datetime.date(year=1933, month=12, day=26)
}

test_driver = {
    'id': 1,
    'name': "Sanic",
    'birthday': datetime.date(year=2010, month=3, day=31)
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
