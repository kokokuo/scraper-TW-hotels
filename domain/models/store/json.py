import json
import re
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

    async def store_hotels(self,
                           county_name: str,
                           hotels: List[HotelContentRow]) -> None:
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
