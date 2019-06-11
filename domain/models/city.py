from typing import List
from .county import CountyVO


class CityVO(object):
    def __init__(self, name: str, code: str, counties: List[CountyVO]):
        self._set_name(name)

    def _set_name(self, name: str):
        self._name = name

    def _set_code(self, code: str):
        self._code = code

    def _set_counties(self, counties: List[CountyVO]):
        self._counties = counties

    @property
    def name(self) -> str:
        return self._name

    @property
    def code(self) -> str:
        return self._code

    @property
    def counties(self) -> List[CountyVO]:
        return self._counties

    def __eq__(self, other: object):
        if not isinstance(other, CityVO):
            return False
        if self.name == other.name and self.code == other.code:
            return True
        return False

    def __repr__(self):
        return "<CityVO: name=%r, code=%r, counties=%r>" % (self.name, self.code, self.counties)