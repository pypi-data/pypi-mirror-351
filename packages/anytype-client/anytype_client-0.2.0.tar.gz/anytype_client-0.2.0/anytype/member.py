from .api import apiEndpoints, APIWrapper


class Member(APIWrapper):
    def __init__(self):
        self._apiEndpoints: apiEndpoints | None = None
        self.type = ""
        self.id = ""
        self.icon = ""
        self.name = ""

    def __repr__(self):
        return f"<Member(type={self.name})>"
