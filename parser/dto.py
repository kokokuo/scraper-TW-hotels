from dataclasses import dataclass
from typing import Optional, Dict
from enum import Enum


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


class HotelField(Enum):
    Id = u"旅館ID"
    Name = u"旅宿民稱"
    Address = u"地址"
    Phone = u"訂房專線"
    Url = u"網址"
    Email = u"電子信箱"
    Rooms = u"總房間數"
    Prices = u"定價"


HotelInfo = Dict[HotelField, str]
