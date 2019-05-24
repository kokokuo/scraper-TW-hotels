from dataclasses import dataclass
from typing import Optional


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


@dataclass
class HotelInfo(object):
    """
    爬取的旅館資訊
    Args:
        name (str): 旅館名稱
        phone (str): 聯絡電話
        address (str): 地址
        room (int): 房間數
        prices (str): 價錢範圍
        email (str): 信箱
        siteurl (str): 網站連結
    """
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    room: Optional[str] = None
    prices: Optional[str] = None
    email: Optional[str] = None
    siteurl: Optional[str] = None
