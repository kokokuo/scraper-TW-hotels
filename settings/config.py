# -*- coding: utf-8 -*-
from typing import List
from apps.dto.hotel import HotelField


class Config(object):
    WEBSITE_URL = "https://taiwanstay.net.tw"
    CITIES_CODE = {
        "F": "新北市", "A": "臺北市", "H": "桃園市", "B": "臺中市", "R": "臺南市",
        "S": "高雄市", "G": "宜蘭縣", "J": "新竹縣", "K": "苗栗縣", "N": "彰化縣",
        "M": "南投縣", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "V": "臺東縣",
        "U": "花蓮縣", "X": "澎湖縣", "C": "基隆市", "O": "新竹市", "I": "嘉義市",
        "W": "金門縣", "Z": "連江縣"
    }
    CITY_SELECTOR_XPATH = "//*[@id='sel_city']"
    COUNTIES_OPTION_XPATH = "//*[@id='sel_area']/option"
    HOTEL_HREF_XPATH = "//*[@id='searchpage']/div/div/div[3]/div/div/a/@href"
    WEBSITE_URL = "https://taiwanstay.net.tw"
    SEARCH_ROUNTE = "/tourism_web/search.php"
    HOTEL_CONTENT_ROUTE = "/tourism_web/hotel_content.php"
    ABNORMAL_ROUTE = "/system_abnormal.php"
    SEARCH_URL = WEBSITE_URL + SEARCH_ROUNTE
    HOTEL_CONTENT_URL = WEBSITE_URL + HOTEL_CONTENT_ROUTE
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

    HOTELS_COMMON_SERACH_PARAMS = {
        "page": 1,
        "sortBy": "",
        "act": "",
        "sel_hotel[]": [1, 2, 3],
        "sel_keyword": "",
        "sel_city": "",
        "sel_keyword": "",
        "sel_city": "",
        "sel_area": "",
        "sel_price": "",
        "sel_room_num": "",
        "sel_type": "",
    }

    HOTEL_CONTENT_XPATH = {
        HotelField.Name: "//*[@id='right-hotel']/h2/text()",
        HotelField.Address: "//*[@id='right-hotel']/div[4]/div[2]/p/span[2]/text()",
        HotelField.Phone: "//*[@id='tel_div']/p/span[2]/text()",
        HotelField.Email: "//*[@id='email_div']/a/p/span[2]/text()",
        HotelField.Rooms: "//*[@id='right-hotel']/div[5]/div[2]/p/span[2]/text()",
        HotelField.Prices: "//*[@id='right-hotel']/div[5]/div[3]/p/span[2]/text()",
        HotelField.Url: "//*[@id='website_div']/p/span[2]/a"
    }
