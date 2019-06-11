# -*- coding: utf-8 -*-
from typing import List


class CountyVO(object):
    def __init__(self, name: str, value: int) -> None:
        self._set_value(value)
        self._set_name(name)

    def _set_name(self, name: str):
        self._name = name

    def _set_value(self, value: int):
        self._value = value

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> int:
        return self._value

    def __eq__(self, other: object):
        if not isinstance(other, CountyVO):
            return False
        if self.name == other.name and self.value == other.value:
            return True
        return False

    def __repr__(self):
        return "<CountyVO: name=%r, value=%r>" % (self.name, self.value)
