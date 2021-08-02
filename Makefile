pretty:
	black --line-length 79 --target-version=py39 sanic_openapi tests
	isort --line-length 79 --trailing-comma -m 3 sanic_openapi tests
