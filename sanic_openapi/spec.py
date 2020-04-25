from typing import Dict, get_type_hints
from itertools import chain

from sanic_openapi.doc import (
    serialize_schema, Field, Object, String, UUID, List, JsonBody, Dictionary, File,
    DateTime, Date, Boolean, Tuple, Float, Integer
)


SIMPLE_TYPES = (
    Field, String, UUID, List, JsonBody, Dictionary, File, DateTime, Date, Boolean,
    Tuple, Float, Integer
)


class Spec:
    def __init__(self, config) -> None:
        self.config = config
        self.swagger = "2.0"
        self._tags = {}
        self._paths = {}
        self._definitions = {}

    @property
    def info(self):
        return {
            "version": getattr(self.config, "API_VERSION", "1.0.0"),
            "title": getattr(self.config, "API_TITLE", "API"),
            "description": getattr(self.config, "API_DESCRIPTION", ""),
            "termsOfService": getattr(self.config, "API_TERMS_OF_SERVICE", ""),
            "contact": {"email": getattr(self.config, "API_CONTACT_EMAIL", None)},
            "license": {
                "name": getattr(self.config, "API_LICENSE_NAME", None),
                "url": getattr(self.config, "API_LICENSE_URL", None),
            },
        }

    @property
    def schemes(self):
        return getattr(self.config, "API_SCHEMES", ["http"])

    @property
    def host(self):
        return getattr(self.config, "API_HOST", None)

    @property
    def basePath(self):
        return getattr(self.config, "API_BASEPATH", None)

    # --------------------------------------------------------------- #
    # Authorization
    # --------------------------------------------------------------- #

    @property
    def securityDefinitions(self):
        return getattr(self.config, "API_SECURITY_DEFINITIONS", None)

    @property
    def security(self):
        return getattr(self.config, "API_SECURITY", None)

    @property
    def definitions(self):
        return self._definitions

    @property
    def tags(self):
        return self._tags

    @property
    def paths(self):
        return self._paths

    def _build_definition(self, definition):
        for key, schema in chain(
            {key: getattr(definition, key) for key in dir(definition)}.items(),
            get_type_hints(definition).items(),
        ):
            if key.startswith("_"):
                continue
            if isinstance(schema, (list, tuple)):
                for s in schema:
                    if get_type_hints(s):
                        self._build_definition(s)

            elif isinstance(schema, SIMPLE_TYPES):
                pass

            elif get_type_hints(schema):
                self._build_definition(schema)

            self._definitions.setdefault(definition.__name__, {
                "type": "object",
                "properties": {},
            })
            self._definitions[definition.__name__]["properties"][key] = serialize_schema(schema)

    def add_definitions(self, definitions):
        if isinstance(definitions, list):
            for definition in definitions:
                self._build_definition(definition)
        elif isinstance(definitions, type):
            self._build_definition(definitions)
        elif isinstance(definitions, Object):
            self._definitions = {**self.definitions, **definitions.definitions}
        elif isinstance(definitions, SIMPLE_TYPES):
            if definitions.name:
                self._definitions[definitions.name] = definitions.serialize()
        elif isinstance(definitions, dict):
            self._definitions = {**self.definitions, **definitions}
        else:
            raise NotImplementedError

    def add_tags(self, tags):
        self._tags = tags

    def add_paths(self, paths):
        self._paths = paths

    @property
    def as_dict(self) -> Dict:
        return {
            "swagger": self.swagger,
            "info": self.info,
            "schemes": self.schemes,
            "host": self.host,
            "basePath": self.basePath,
            "securityDefinitions": self.securityDefinitions,
            "security": self.security,
            "definitions": self.definitions,
            "tags": self.tags,
            "paths": self.paths,
        }
