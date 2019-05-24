# -*- coding: utf-8 -*-
from collections import namedtuple


WEBSITE_URL = "https://taiwanstay.net.tw"

County = namedtuple("County", ["code", "text"])

# 網頁的查詢參數
PAYLOAD = {
    "page": 1,
    "sortBy": None,
    "act": None,
    "sel_hotel[]": None,
    "sel_hotel[]": None,
    "sel_hotel[]": None,
    "sel_keyword": None,
    "sel_city": None,
    "sel_keyword": None,
    "sel_city": None,
    "sel_area": None,
    "sel_price": None,
    "sel_room_num": None,
    "sel_type": None,
}
