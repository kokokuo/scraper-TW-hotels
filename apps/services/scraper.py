# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
import os
import re
import random
import time
import asyncio
import aiohttp
import logging
from logging import StreamHandler
from urllib import parse
from http.cookies import SimpleCookie
from types import CoroutineType
from typing import List, Dict, MutableMapping, Optional
from lxml import etree
from tenacity import retry
from tenacity import retry_if_exception_type, stop_after_attempt, wait_fixed
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from store.excel import ExcelStore
from apps.dto.resp import SyncHttpResponse
from apps.dto.hotel import HotelInfo, HotelField
from apps.dto.county import CountyOption, TotalPageOfCounty
from domain.models.county import CountyVO
from domain.services.parsers import CountiesParser
from settings.config import Config
from parser.excepts import ReqSysAbnoramlError


class TaiwanHotelsScrapingService(object):
    def __init__(self, conf: Config) -> None:
        self._conf = conf
        self._params: dict = {
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
        fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        self._logger = self._console_logger(__name__, logging.DEBUG, fmt)

    def _console_logger(self, name: str, level: int, fmt: str):
        logger = logging.getLogger(name)
        handler = StreamHandler()
        handler.setLevel(level)
        formatter = logging.Formatter(fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
        return logger

    def find_counties(self, city_name: str) -> List[CountyVO]:
        """
        抓取指定的縣市 City 名稱
        Returns:
            List[CountyOption]: 此城市的所有省區
        """
        counties_parser = CountiesParser(self._conf.WEBSITE_URL)
        counties: List[CountyVO] = counties_parser.extract_counties(city_name)
        self._logger.info(f"完成網頁模擬，選擇縣市: {city_name}，取得「{city_name}」所有的市區鄉鎮")
        return counties

    def find_hotels_of_counties(self, city_name, county: List[CountyVO]):
        pass

    def find_hotels_by_county(self, city_name, county: CountyVO):
        pass