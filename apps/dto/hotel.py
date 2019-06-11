# -*- coding: utf-8 -*-
from enum import Enum
from typing import Dict


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

