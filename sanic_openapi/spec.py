from sanic import Sanic


class Spec:
    def __init__(self, app: Sanic) -> None:
        self.swagger = "2.0"

        self.info = {
            "version": getattr(app.config, "API_VERSION", "1.0.0"),
            "title": getattr(app.config, "API_TITLE", "API"),
            "description": getattr(app.config, "API_DESCRIPTION", ""),
            "termsOfService": getattr(app.config, "API_TERMS_OF_SERVICE", ""),
            "contact": {"email": getattr(app.config, "API_CONTACT_EMAIL", None)},
            "license": {
                "name": getattr(app.config, "API_LICENSE_NAME", None),
                "url": getattr(app.config, "API_LICENSE_URL", None),
            },
        }
        self.schemes = getattr(app.config, "API_SCHEMES", ["http"])

        self.host = getattr(app.config, "API_HOST", None)

        self.basePath = getattr(app.config, "API_BASEPATH", None)

        # --------------------------------------------------------------- #
        # Authorization
        # --------------------------------------------------------------- #

        self.securityDefinitions = getattr(app.config, "API_SECURITY_DEFINITIONS", None)
        self.security = getattr(app.config, "API_SECURITY", None)

        self.definitions = {}
        self.tags = []
        self.paths = {}

    def add_definitions(self, definitions):
        self.definitions = definitions

    def add_tags(self, tags):
        self.tags = tags

    def add_paths(self, paths):
        self.paths = paths

    @property
    def as_dict(self):
        return self.__dict__
