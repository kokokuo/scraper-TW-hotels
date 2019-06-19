# -*- coding: utf-8 -*-
from typing import List
from logging import Logger
from apps.dto.hotel import HotelContentRow
from domain.models.hotel.field import HotelField
from domain.models.store.excel import HotelsExcelStorer
from domain.models.store.json import HotelsJsonStorer
from settings.config import Config


class HotelStoringExcelService(object):
    def __init__(self, filename: str, scraping_logger: Logger) -> None:
        self._logger = scraping_logger
        self._excel = HotelsExcelStorer(filename, self._logger)

    async def store(self,
                    county_name: str,
                    parsed_columns: List[HotelField],
                    hotels: List[HotelContentRow],
                    filename: str):
        try:
            excel = HotelsExcelStorer(filename, self._logger)
            # 新增此市區鄉鎮的 Sheet
            sheet = self._excel.add_sheet(county_name, parsed_columns)
            self._logger.info(f" [ Saving ]    寫入 {county_name} 資料至 Excel 中....")
            await self._excel.store_hotels(sheet, parsed_columns, hotels)
            excel.close()
            self._logger.info(f" [ Saved  ]    寫入 {county_name} 的旅館資料至 Excel 完成。")
        except Exception as e:
            self._logger.error(" [ ERROR ]    寫入 Excel 異常 ！ ")
            raise e

    def close(self):
        self._excel.close()


class HotelStoringJsonService(object):
    def __init__(self, scraping_logger: Logger) -> None:
        self._logger = scraping_logger

    async def store(self,
                    county_name: str,
                    hotels: List[HotelContentRow],
                    filename: str):
        try:
            jsoner = HotelsJsonStorer(filename, self._logger)
            self._logger.info(f" [ Saving ]    寫入 {county_name} 資料至 Json 中....")
            await jsoner.store_hotels(county_name, hotels)
            self._logger.info(f" [ Saved  ]    寫入 {county_name} 的旅館資料至 Json 完成。")
        except Exception as e:
            self._logger.error(" [ ERROR ]    寫入 Json 異常 ！ ")
            raise e
