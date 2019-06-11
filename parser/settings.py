# -*- coding: utf-8 -*-
from typing import List
from parser.dto import HotelField


class TaiwanHotelConfig(object):
    WEBSITE_URL = "https://taiwanstay.net.tw"
    CITIES_CODE = {
        "F": "新北市", "A": "臺北市", "H": "桃園市", "B": "臺中市", "R": "臺南市",
        "S": "高雄市", "G": "宜蘭縣", "J": "新竹縣", "K": "苗栗縣", "N": "彰化縣",
        "M": "南投縣", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "V": "臺東縣",
        "U": "花蓮縣", "X": "澎湖縣", "C": "基隆市", "O": "新竹市", "I": "嘉義市",
        "W": "金門縣", "Z": "連江縣"
    }

    WEBSITE_URL = "https://taiwanstay.net.tw"
    SEARCH_ROUNTE = "/tourism_web/search.php"
    HOTEL_PAGE_ROUTE = "/tourism_web/hotel_content.php"
    ABNORMAL_ROUTE = "/system_abnormal.php"
    SEARCH_URL = WEBSITE_URL + SEARCH_ROUNTE
    HOTEL_PAGE_URL = WEBSITE_URL + HOTEL_PAGE_ROUTE
    ABNORMAL_URL = WEBSITE_URL + ABNORMAL_ROUTE

    PARSED_COLUMNS: List[HotelField] = [
        HotelField.Name,
        HotelField.Address,
        HotelField.Phone,
        HotelField.Email,
        HotelField.Rooms,
        HotelField.Prices,
        HotelField.Url
    ]
