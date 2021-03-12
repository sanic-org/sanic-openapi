from sanic import Sanic

from .definitions import Components


class Spec:
    def __init__(self, app: Sanic) -> None:
        self.openapi = "3.0.0"

        self.info = {
            "version": getattr(app.config, "API_VERSION", "1.0.0"),
            "title": getattr(app.config, "API_TITLE", "API"),
            "description": getattr(app.config, "API_DESCRIPTION", ""),
            "termsOfService": getattr(app.config, "API_TERMS_OF_SERVICE", ""),
            "contact": {
                "name": getattr(app.config, "API_CONTACT_NAME", None),
                "url": getattr(app.config, "API_CONTACT_URL", None),
                "email": getattr(app.config, "API_CONTACT_EMAIL", None),
            },
            "license": {
                "name": getattr(app.config, "API_LICENSE_NAME", None),
                "url": getattr(app.config, "API_LICENSE_URL", None),
            },
        }
        host = getattr(app.config, "API_HOST", "localhost")
        basePath = getattr(app.config, "API_BASEPATH", "")
        self.servers = [
            {
                "url": "{}://{}/{}".format(scheme, host, basePath),
                "description": getattr(app.config, "API_DESCRIPTION", None),
            }
            for scheme in getattr(app.config, "API_SCHEMES", ["http"])
        ]

        securityDefinitions = getattr(app.config, "API_SECURITY_DEFINITIONS", None)

        self.components = getattr(
            app.config, "API_COMPONENTS", Components(securitySchemes=securityDefinitions)
        ).serialize()

        self.security = getattr(app.config, "API_SECURITY", None)

        # tags: List[Tag]
        self.tags = []

        # paths: Dict[str, PathItem]
        self.paths = {}

    def add_definitions(self, definitions):
        # self.definitions = definitions  # old way
        self.components["schemas"] = definitions or {}  # todo -- rewrite

    def add_tags(self, tags):
        self.tags = tags

    def add_paths(self, paths):
        self.paths = paths

    @property
    def as_dict(self):
        return self.__dict__
