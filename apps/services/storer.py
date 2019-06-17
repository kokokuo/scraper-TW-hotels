# -*- coding: utf-8 -*-
from typing import List
from logging import Logger
from apps.dto.hotel import HotelFieldRow
from domain.models.hotel.field import HotelField
from domain.models.store.excel import ExcelStore
from infra.logging import scraping_logger
from settings.config import Config


class HotelContentVOsStoringService(object):
    def __init__(self, scraping_logger: Logger) -> None:
        self._logger = scraping_logger

    async def store2excel(self,
                          county_name: str,
                          fields: List[HotelField],
                          hotels: List[HotelFieldRow],
                          filename: str):
        try:
            excel = ExcelStore(filename, self._logger)
            # 新增此市區鄉鎮的 Sheet
            sheet = excel.add_sheet(county_name, Config.PARSED_COLUMNS)
            self._logger.info(f" [ Saving ]       寫入 {county_name} 資料至 Excel 中....")
            # 抓出每一的鄉鎮的所有頁面資料
            hotel: HotelFieldRow
            for idx, hotel in enumerate(hotels):
                # 第 0 列為 Header，所以 idx 需要 + 1
                await excel.store_row(sheet, idx + 1, Config.PARSED_COLUMNS, hotel)
            self._logger.info(f" [ Saved ]      寫入 {county_name} 的旅館資料完成。")
        except Exception as e:
            self._logger.error(" [ ERROR ]      寫入 Excel 異常 ！ ")
            raise e


hotel_storing_service = HotelContentVOsStoringService(scraping_logger)
