import pytest
from sanic import Sanic
from sanic.response import json_dumps
from sanic_openapi import openapi, openapi_blueprint, doc


def get_app():

    app = Sanic()
    app.blueprint(openapi_blueprint)

    return app


def get_spec(app, exclude):

    openapi.build_spec(app, None)

    return {k:v for k,v in openapi._spec.items() if k not in exclude}


def dump(data):
    print(json_dumps(data, indent=4, sort_keys=True))
    raise



# ------------------------------------------------------------ #
#  GET
# ------------------------------------------------------------ #

def test_get_list():

    app = get_app()

    @app.put('/test', strict_slashes=True)
    @doc.consumes(doc.List(int, description="All the numbers"), location="body")
    def test(request):
        pass

    output = get_spec(app, exclude=['schemes', 'tags', 'info'])

    # dump(output)

    assert {
            "definitions": {},
            "paths": {
                "/test": {
                    "put": {
                        "consumes": [
                            "application/json"
                        ],
                        "operationId": "test",
                        "parameters": [
                            {
                                "in": "body",
                                "items": {
                                    "format": "int64",
                                    "type": "integer"
                                },
                                "name": None,
                                "required": False,
                                "type": "array"
                            }
                        ],
                        "produces": [
                            "application/json"
                        ],
                        "responses": {
                            "200": {}
                        }
                    }
                }
            },
            "swagger": "2.0"
        } == output


def test_get_detail():

    app = get_app()

    class Child:
        id = int

    class Item:
        name = str
        child = Child
        children = [Child]

    @app.put('/test/<id:int>', strict_slashes=True)
    @doc.route(produces=Item, summary="Fetch an item")
    def test(request):
        pass

    output = get_spec(app, exclude=['info', 'schemes', 'tags'])

    # dump(output)

    assert {
        "definitions":{
            "Child":{
                "properties":{
                    "id":{
                        "format":"int64",
                        "type":"integer"
                    }
                },
                "type":"object"
            },
            "Item":{
                "properties":{
                    "child":{
                        "$ref":"#/definitions/Child",
                        "type":"object"
                    },
                    "children":{
                        "items":{
                            "$ref":"#/definitions/Child",
                            "type":"object"
                        },
                        "type":"array"
                    },
                    "name":{
                        "type":"string"
                    }
                },
                "type":"object"
            }
        },
        "paths":{
            "/test/{id}":{
                "put":{
                    "consumes":[
                        "application/json"
                    ],
                    "operationId":"test",
                    "parameters":[
                        {
                            "format":"int64",
                            "in":"path",
                            "name":"id",
                            "required":True,
                            "type":"integer"
                        }
                    ],
                    "produces":[
                        "application/json"
                    ],
                    "responses":{
                        "200":{
                            "schema":{
                                "$ref":"#/definitions/Item",
                                "type":"object"
                            }
                        }
                    },
                    "summary":"Fetch an item"
                }
            }
        },
        "swagger":"2.0"
    } == output



# ------------------------------------------------------------ #
#  POST
# ------------------------------------------------------------ #

def test_post():

    app = get_app()

    class Item:
        foo = int


    @app.post('/test/', strict_slashes=True)
    @doc.summary("Create an item")
    @doc.consumes(Item)
    @doc.produces(Item)
    def test(request):
        pass

    output = get_spec(app, exclude=['info', 'schemes', 'tags'])

    # dump(output)

    assert {
        "definitions":{
            "Item":{
                "properties":{
                    "foo":{
                        "format":"int64",
                        "type":"integer"
                    }
                },
                "type":"object"
            }
        },
        "paths":{
            "/test/":{
                "post":{
                    "consumes":[
                        "application/json"
                    ],
                    "operationId":"test",
                    "parameters":[
                        {
                            "in":"query",
                            "name":"body",
                            "required":False,
                            "schema":{
                                "$ref":"#/definitions/Item"
                            },
                            "type":"object"
                        }
                    ],
                    "produces":[
                        "application/json"
                    ],
                    "responses":{
                        "200":{
                            "schema":{

                            }
                        }
                    },
                    "summary":"Create an item"
                }
            }
        },
        "swagger":"2.0"
    } == output



# ------------------------------------------------------------ #
#  DELETE
# ------------------------------------------------------------ #

def test_delete():

    app = get_app()

    class Status:
        success = bool

    @app.delete('/test/<id:int>', strict_slashes=True)
    @doc.summary("Delete an item")
    @doc.produces(Status)
    def test(request):
        pass

    output = get_spec(app, exclude=['info', 'schemes', 'tags'])

    # dump(output)

    # todo: this is incorrect. https://github.com/huge-success/sanic-openapi/issues/50

    assert {
        "definitions":{

        },
        "paths":{
            "/test/{id}":{
                "delete":{
                    "consumes":[
                        "application/json"
                    ],
                    "operationId":"test",
                    "parameters":[
                        {
                            "format":"int64",
                            "in":"path",
                            "name":"id",
                            "required":True,
                            "type":"integer"
                        }
                    ],
                    "produces":[
                        "application/json"
                    ],
                    "responses":{
                        "200":{
                            "schema":{

                            }
                        }
                    },
                    "summary":"Delete an item"
                }
            }
        },
        "swagger":"2.0"
    } == output
