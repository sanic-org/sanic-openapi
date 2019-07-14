# Configurations

Sanic-OpenAPI provides following configurable items:

* API information
* Authentication(Security Definitions)
* URI filter
* Swagger UI configurations

## API information

You can provide some additional information of your APIs by using Sanic-OpenAPI configurations.
For more detail of those additional information, please check the [document](https://swagger.io/specification/#infoObject) from Swagger.

### API_VERSION

* Key: `API_VERSION`
* Type: `str`
* Default: `1.0.0`
* Usage:

    ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_VERSION"] = "0.1.0"

    ```

* Result:
  ![](../_static/images/configurations/API_VERSION.png)

### API_TITLE

* Key: `API_TITLE`
* Type: `str`
* Default: `API`
* Usage:

    ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_TITLE"] = "Sanci-OpenAPI"

    ```

* Result:
  ![](../_static/images/configurations/API_TITLE.png)

### API_DESCRIPTION

* Key: `API_DESCRIPTION`
* Type: `str`
* Deafult: `""`
* Usage:

    ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_DESCRIPTION"] = "An example Swagger from Sanic-OpenAPI"

    ```

* Result:
  ![](../_static/images/configurations/API_DESCRIPTION.png)

### API_TERMS_OF_SERVICE

* Key: `API_TERMS_OF_SERVICE`
* Type: `str` of a URL
* Deafult: `""`
* Usage:

  ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_TERMS_OF_SERVICE"] = "https://github.com/huge-success/sanic-openapi/blob/master/README.md"

  ```

* Result:
  ![](../_static/images/configurations/API_TERMS_OF_SERVICE.png)

### API_CONTACT_EMAIL

* Key: `API_CONTACT_EMAIL`
* Type: `str` of email address
* Deafult: `None"`
* Usage:

    ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_CONTACT_EMAIL"] = "foo@bar.com"

    ```

* Result:
  ![](../_static/images/configurations/API_CONTACT_EMAIL.png)

### API_LICENSE_NAME

* Key: `API_LICENSE_NAME`
* Type: `str`
* Default: `None`
* Usage:

    python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_LICENSE_NAME"] = "MIT"

    

* Result:
  ![](../_static/images/configurations/API_LICENSE_NAME.png)

### API_LICENSE_URL

* Key: `API_LICENSE_URL`
* Type: `str` of URL
* Default: `None`
* Usgae:

    ```python
    from sanic import Sanic
    from sanic_openapi import swagger_blueprint

    app = Sanic()
    app.blueprint(swagger_blueprint)
    app.config["API_LICENSE_URL"] = "https://github.com/huge-success/sanic-openapi/blob/master/LICENSE"

    ```

* Result:
  ![](../_static/images/configurations/API_LICENSE_URL.png)

## Authentication

## URI filter

## Swagger UI configurations