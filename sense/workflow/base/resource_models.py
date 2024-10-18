from abc import ABC
from collections import namedtuple
from typing import List


class Resource(ABC):
    def __init__(self, label, name: str):
        self.label = label
        self.name = name
        self._depends_on: List[str] = list()

    def get_label(self) -> str:
        return self.label

    def get_name(self) -> str:
        return self.name

    def set_externally_depends_on(self, depends_on: List[str]):
        self._depends_on = depends_on

    def get_externally_depends_on(self) -> List[str]:
        return self._depends_on


class Service(Resource):
    def __init__(self, *, label, name: str):
        super().__init__(label, name)


ResolvedDependency = namedtuple("ResolvedDependency", "resource_label attr value")
