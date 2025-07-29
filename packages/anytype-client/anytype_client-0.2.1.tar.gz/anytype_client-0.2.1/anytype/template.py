from .api import apiEndpoints, APIWrapper


class Template(APIWrapper):
    def __init__(self):
        self._apiEndpoints: apiEndpoints | None = None
        self.type = ""
        self.id = ""
        self.name = ""
        self.icon = ""

    def __repr__(self):
        return f"<Template(name={self.name}, icon={self.icon})>"
