
# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class CountyOption(object):
    """
    市區鄉鎮的選項資料
    Args:
        name (str): 此選項的名稱
        value (int): 對應的 id 值
    """
    name: str
    value: int


@dataclass
class TotalPageOfCounty(object):
    """
    Args:
        pages (int): 該市區鄉鎮的所有頁數
        total_hotels (int): 該市區鄉鎮的所有旅館數
    """
    pages: int
    num_of_hotels: int
