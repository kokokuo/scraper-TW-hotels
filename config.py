#!/usr/bin/python
# -*- coding: utf-8 -*-
from collections import namedtuple

ROOT_URL = 'http://taiwanstay.net.tw'

County = namedtuple('County', ['code', 'text'])

# 城市代碼，可以重此切換
CITY_CODE = 'R'

# 網頁的查詢參數
PAYLOAD = {
	'hotelCity': None, 
	'hotelCounty': None,
	'host': False,
	'conference': False, 
	'accessible':False,
	'accessibility': False,
	'roompricelow':False,
	'page':1,
	'listPage':10
}