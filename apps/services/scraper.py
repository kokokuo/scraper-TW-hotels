# -*- coding: utf-8 -*-
from typing import List
from logging import Logger
from domain.models.region.selector import counties_selector
from domain.models.region.county import CountyVO
from domain.models.hotel.parsers import pages_parser, hotels_of_county_parser
from domain.models.hotel.pages import PagesOfHotelVO
from domain.models.hotel.content import HotelContentVO
from infra.logging import scraping_logger
from settings.config import Config
from infra.excepts import ReqSysAbnoramlError


class TaiwanHotelsScrapingService(object):
    def __init__(self, scraping_logger: Logger) -> None:
        self._logger = scraping_logger

    async def find_counties(self, city_name: str) -> List[CountyVO]:
        """
        抓取指定的縣市 City 名稱
        Returns:
            List[CountyVO]: 此城市的所有省區
        """
        counties: List[CountyVO] = await counties_selector.extract(city_name)
        return counties

    async def find_hotels_by_county(self, city_name: str, county: CountyVO) -> List[HotelContentVO]:
        """
        找出此城市指定的鄉鎮市區內所有旅館資料
        Args:
            city_name (str): 城市名
            county (CountyVO): 鄉鎮市區的 ValueObject

        Returns:
            List[HotelContentVO]: 抓取下來的旅館資料列表
        """
        pages: PagesOfHotelVO = await pages_parser.extract(city_name, county)
        self._logger.info(f" [ Scraping ]       開始抓: {city_name} {county.name} ##########")
        hotels: List[HotelContentVO] = await hotels_of_county_parser.extract_all(city_name, county, pages)
        return hotels


hotels_scraping_service = TaiwanHotelsScrapingService(scraping_logger)
