import os

from sanic.blueprints import Blueprint

dir_path = os.path.dirname(os.path.realpath(__file__))
dir_path = os.path.abspath(dir_path + '/ui')

blueprint = Blueprint('swagger', url_prefix='swagger')

blueprint.static('/', dir_path + '/index.html')
blueprint.static('/', dir_path)
