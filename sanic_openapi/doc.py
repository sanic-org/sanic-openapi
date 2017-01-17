from collections import defaultdict


class Field:
    def __init__(self, name=None, description=None, required=None):
        self.name = name
        self.description = description
        self.required = required

    def serialize(self):
        output = {}
        if self.name:
            output['name'] = self.name
        if self.description:
            output['description'] = self.description
        if self.required is not None:
            output['required'] = self.required
        return output


class Integer(Field):
    def serialize(self):
        return {
            "type": "integer",
            "format": "int64",
            **super().serialize()
        }


class String(Field):
    def serialize(self):
        return {
            "type": "string",
            **super().serialize()
        }


class Tuple(Field):
    pass


class Dictionary(Field):
    def __init__(self, fields=None):
        self.fields = fields or {}

    def serialize(self):
        return {
            "type": "object",
            "properties": {key: serialize_schema(schema) for key, schema in self.fields.items()},
            **super().serialize()
        }


class List(Field):
    def __init__(self, items=None, *args, **kwargs):
        self.items = items or []
        super().__init__(*args, **kwargs)

    def serialize(self):
        if len(self.items) > 1:
            return Tuple(self.items).serialize()
        elif self.items:
            return Tuple(self.items).serialize()


class Object(Field):
    def __init__(self, cls, *args, object_name=None, **kwargs):
        self.cls = cls
        self.object_name = object_name or cls.__name__
        super().__init__(*args, **kwargs)

    def serialize(self, reference=False):
        if reference:
            return {
                "schema": {
                    "$ref": "#/definitions/{}".format(self.object_name)
                },
                **super().serialize()
            }
        else:
            print("INLINE")
            return {
                "type": "object",
                "properties": {
                    key: serialize_schema(schema)
                    for key, schema in self.cls.__dict__.items()
                    if not key.startswith("_")
                },
                **super().serialize()
            }


class RouteSpec:
    consumes = None
    consumes_content_type = None
    produces = None
    produces_content_type = None
    summary = None
    description = None
    operation = None


types = {}


def serialize_schema(schema):
    schema_type = type(schema)

    # --------------------------------------------------------------- #
    # Class
    # --------------------------------------------------------------- #
    if schema_type is type:
        if issubclass(schema, Field):
            return schema().serialize()
        elif schema is dict:
            return Dictionary().serialize()
        elif schema is list:
            return List().serialize()
        elif schema is int:
            return Integer().serialize()
        elif schema is str:
            return String().serialize()
        else:
            return Object(schema).serialize()

    # --------------------------------------------------------------- #
    # Object
    # --------------------------------------------------------------- #
    else:
        if issubclass(schema_type, Field):
            return schema.serialize()
        elif schema_type is dict:
            return Dictionary(schema).serialize()
        elif schema_type is list:
            return List(schema).serialize()

    return {}

# types = {}
# def register_types(obj):
#     obj_type = type(obj)
#     if obj_type is type:
#         types[obj] = True
#     if issubclass(obj_type, Field):
#         register_types(obj.types())
#     if issubclass(obj_type, list):
#         for sub_obj in obj:
#             register_types(sub_obj)

route_specs = defaultdict(RouteSpec)


def summary(text):
    def inner(func):
        route_specs[func].summary = text
        return func
    return inner


def description(text):
    def inner(func):
        route_specs[func].description = text
        return func
    return inner


def consumes(*args, content_type=None):
    def inner(func):
        if args:
            route_specs[func].consumes = args[0] if len(args) == 1 else args
            route_specs[func].consumes_content_type = content_type
        return func
    return inner


def produces(*args, content_type=None):
    def inner(func):
        if args:
            route_specs[func].produces = args[0] if len(args) == 1 else args
            route_specs[func].produces_content_type = content_type
        return func
    return inner
