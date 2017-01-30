from sanic import Sanic
from sanic_openapi import swagger_blueprint, openapi_blueprint
from blueprints.car import blueprint as car_blueprint
from blueprints.driver import blueprint as driver_blueprint
from blueprints.garage import blueprint as garage_blueprint
from blueprints.manufacturer import blueprint as manufacturer_blueprint

app = Sanic()

app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)
app.blueprint(car_blueprint)
app.blueprint(driver_blueprint)
app.blueprint(garage_blueprint)
app.blueprint(manufacturer_blueprint)

app.config.API_VERSION = '1.0.0'
app.config.API_TITLE = 'Car API'
app.config.API_TERMS_OF_SERVICE = 'Use with caution!'
app.config.API_CONTACT_EMAIL = 'channelcat@gmail.com'

app.run(debug=True)
