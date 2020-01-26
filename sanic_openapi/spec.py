from typing import Dict


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

    def add_definitions(self, definitions):
        for key, value in definitions.items():
            self._definitions[key] = value

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
