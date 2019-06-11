from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict
from yarl import URL
from multidict import CIMultiDictProxy
from http.cookies import SimpleCookie


@dataclass
class SyncHttpResponse(object):
    """
    已經同步後取區 aiohttp 返回的 ClientResponse 資料
    Args:
        raw_content (bytes): Bytes 格式的 HTML 內容
        text (str): Str 格式的 HTML 內容
        status_code (str): 狀態碼
        headers (dict): 回傳的 Headers
        cookies (dict): 回傳的 Cookies
        url (URL): 回傳的 URL
    """
    raw_content: bytes
    text: str
    status_code: int
    headers: dict
    cookies: dict
    url: str


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
