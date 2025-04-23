from abc import ABC
from collections import namedtuple


class Resource(ABC):
    def __init__(self, label, name: str):
        self.label = label
        self.name = name

    def get_label(self) -> str:
        return self.label

    def get_name(self) -> str:
        return self.name


class Service(Resource):
    def __init__(self, *, label, name: str):
        super().__init__(label, name)


ResolvedDependency = namedtuple("ResolvedDependency", "resource_label attr value")
