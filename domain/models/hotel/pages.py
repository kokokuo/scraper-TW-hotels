# -*- coding: utf-8 -*-
from typing import List


class PagesOfHotelVO(object):
    """
    Args:
        pages (int): 該市區鄉鎮的所有頁數
        total_hotels (int): 該市區鄉鎮的所有旅館數
    """
    def __init__(self, pages_num: int, hotels_num: int) -> None:
        self._total = pages_num
        self._hotels_num = hotels_num

    @property
    def total(self) -> int:
        return self._total

    @property
    def hotels_num(self) -> int:
        return self._hotels_num

    def __eq__(self, other: object):
        if not isinstance(other, PagesOfHotelVO):
            return False
        if self.total == other.total and self.hotels_num == other.hotels_num:
            return True
        return False

    def __repr__(self):
        return "<PagesOfHotelVO: total=%r, hotels_num=%r>" % (self.total, self.hotels_num)
