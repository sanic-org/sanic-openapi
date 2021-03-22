from sanic import Sanic


class Spec:
    def __init__(self, app: Sanic) -> None:
        self.swagger = "2.0"

        self.info = {
            "version": getattr(app.config, "API_VERSION", "1.0.0"),
            "title": getattr(app.config, "API_TITLE", "API"),
            "description": getattr(app.config, "API_DESCRIPTION", ""),
            "termsOfService": getattr(app.config, "API_TERMS_OF_SERVICE", ""),
            "license": {
                "name": getattr(app.config, "API_LICENSE_NAME", ""),
                "url": getattr(app.config, "API_LICENSE_URL", ""),
            },
        }

        if hasattr(app.config, "API_CONTACT_EMAIL"):
            self.info["contact"] = {"email": app.config.API_CONTACT_EMAIL}

        self.schemes = getattr(app.config, "API_SCHEMES", ["http"])

        self.host = getattr(app.config, "API_HOST", None)

        self.basePath = getattr(app.config, "API_BASEPATH", None)

        # --------------------------------------------------------------- #
        # Authorization
        # --------------------------------------------------------------- #

        if hasattr(app.config, "API_SECURITY_DEFINITIONS"):
            self.securityDefinitions = app.config.API_SECURITY_DEFINITIONS

        if hasattr(app.config, "API_SECURITY"):
            self.security = app.config.API_SECURITY

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
