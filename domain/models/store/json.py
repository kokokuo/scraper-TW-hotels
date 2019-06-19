import os
import re
import json
from logging import Logger
from io import BytesIO
from collections import OrderedDict
from typing import List, Dict, AnyStr
import aiofiles as aiof
from domain.models.hotel.field import HotelField
from apps.dto.hotel import HotelContentRow


class HotelsJsonStorer(object):
    def __init__(self, filename: str, scraping_logger: Logger) -> None:
        self._logger = scraping_logger
        self._filename = filename

    def _check_json_format(self, data: str) -> bool:
        """
        檢查輸入的資料是否為 Json 格式
        Args:
            data (AnyStr): 來源資料
        Returns:
            bool: 是否比對 json 格式成功
        """
        try:
            if json.loads(data):
                return True
            return False
        except json.JSONDecodeError as e:
            return False

    def _dump_hotels(self,
                     county_name: str,
                     stored_hotels: Dict[str, List[Dict[str, str]]],
                     hotels: List[HotelContentRow]) -> str:
        # 建立該市區鄉鎮的空陣列
        if county_name not in stored_hotels:
            stored_hotels[county_name] = []
        # 寫入資料
        for hotel in hotels:
            data: OrderedDict[str, str] = OrderedDict()
            data[HotelField.Id.value] = hotel[HotelField.Id]
            data[HotelField.Name.value] = hotel[HotelField.Name]
            data[HotelField.Phone.value] = hotel[HotelField.Phone]
            data[HotelField.Address.value] = hotel[HotelField.Address]
            data[HotelField.Rooms.value] = hotel[HotelField.Rooms]
            data[HotelField.Prices.value] = hotel[HotelField.Prices]
            data[HotelField.Email.value] = hotel[HotelField.Email]
            data[HotelField.Url.value] = hotel[HotelField.Url]
            stored_hotels[county_name].append(data)
        result = json.dumps(stored_hotels, ensure_ascii=False, indent=4, sort_keys=True)
        return result

    def _create_empty_json(self, filename: str) -> None:
        """
        建立一個空的 json 檔案
        Args:
            filename (str): 檔案路徑
        """
        pathdir = os.path.dirname(filename)
        if pathdir and not os.path.exists(pathdir):
            os.makedirs(pathdir)
        # 建立空檔案
        open(self._filename, "a").close()

    def _check_existed(self, filename: str) -> bool:
        """
        檢查 Json 檔案是否存在
        Args:
            filename (str): 檔案路徑名稱

        Returns:
            bool: 是否存在
        """
        if os.path.exists(self._filename):
            return True
        return False

    async def store_hotels(self,
                           county_name: str,
                           hotels: List[HotelContentRow]) -> None:
        """
        儲存一批鄉鎮市區的所有旅館資料
        Args:
            county_name (str): 鄉鎮市區名稱
            hotels (List[HotelContentRow]): 該鄉鎮市區的所有旅館資料

        """
        if not self._check_existed(self._filename):
            self._create_empty_json(self._filename)

        async with aiof.open(self._filename, "r+", encoding="utf8") as fp:
            counties_hotels: OrderedDict[str, List[Dict[str, str]]]
            raw_data = await fp.read()
            if raw_data:
                if self._check_json_format(raw_data):
                    counties_hotels = json.loads(raw_data)
                    result = self._dump_hotels(county_name, counties_hotels, hotels)
                    # 清除原先檔案的資料並再寫入
                    await fp.seek(0)
                    await fp.truncate()
                    await fp.write(result)
            else:
                counties_hotels = OrderedDict()
                result = self._dump_hotels(county_name, counties_hotels, hotels)
                await fp.write(result)
