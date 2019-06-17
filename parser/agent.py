# # -*- coding: utf-8 -*-
# import os
# import re
# import random
# import time
# import asyncio
# import aiohttp
# import logging
# from logging import StreamHandler
# from urllib import parse
# from http.cookies import SimpleCookie
# from types import CoroutineType
# from typing import List, Dict, MutableMapping, Optional
# from lxml import etree
# from tenacity import retry
# from tenacity import retry_if_exception_type, stop_after_attempt, wait_fixed
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# from selenium import webdriver
# from selenium.webdriver.remote.webelement import WebElement
# from selenium.webdriver.support.ui import Select
# from domain.models.store.excel import ExcelStore
# from infra.asynchttp.resp import SyncHttpResponse
# from apps.dto.hotel import HotelFieldRow
# from apps.dto.hotel import HotelFieldRow
# from apps.dto.county import CountyOption, TotalPageOfCounty
# from settings.config import Config
# from .excepts import ReqSysAbnoramlError


# class TaiwanHotelParserAgent(object):

#     def __init__(self, selected_code: str) -> None:
#         self._conf = Config
#         self._selected_code: str = selected_code
#         self._params: dict = {
#             "page": 1,
#             "sortBy": "",
#             "act": "",
#             "sel_hotel[]": [1, 2, 3],
#             "sel_keyword": "",
#             "sel_city": "",
#             "sel_keyword": "",
#             "sel_city": "",
#             "sel_area": "",
#             "sel_price": "",
#             "sel_room_num": "",
#             "sel_type": "",
#         }
#         fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
#         self._logger = self._console_logger(__name__, logging.DEBUG, fmt)

#     def _console_logger(self, name: str, level: int, fmt: str):
#         logger = logging.getLogger(name)
#         handler = StreamHandler()
#         handler.setLevel(level)
#         formatter = logging.Formatter(fmt)
#         handler.setFormatter(formatter)
#         logger.addHandler(handler)
#         logger.setLevel(level)
#         return logger

#     def find_counties(self, city_name: str) -> List[CountyOption]:
#         """
#         藉由 Selenium 模擬點擊縣市，取得指定縣市的所有省區資料
#         Returns:
#             List[CountyOption]: 此城市的所有省區
#         """
#         options = webdriver.ChromeOptions()
#         # 不開啟 Browser 的 GUI
#         options.headless = True
#         driver = webdriver.Chrome(chrome_options=options)
#         driver.get(self._conf.WEBSITE_URL)
#         selector: Select = Select(driver.find_element_by_xpath("//*[@id='sel_city']"))
#         selector.select_by_value(city_name)
#         counties_options = driver.find_elements_by_xpath("//*[@id='sel_area']/option")
#         counties: List[CountyOption] = [
#             CountyOption(option.text, option.get_attribute("value"))
#             for option in counties_options if option.get_attribute("value")
#         ]
#         self._logger.info(f"完成網頁模擬，選擇縣市: {city_name}，取得「{city_name}」所有的市區鄉鎮")
#         return counties

#     async def _gen_fake_header(self) -> dict:
#         """
#         產生訪問網頁用的假 Header
#         Returns:
#             [dict]: 產生好的假 Header 標頭
#         """
#         fake_ua = UserAgent()
#         random_ua = random.choice([fake_ua.chrome,
#                                    fake_ua.opera,
#                                    fake_ua.ie,
#                                    fake_ua.firefox,
#                                    fake_ua.safari,
#                                    fake_ua.google,
#                                    fake_ua.ff,
#                                    fake_ua.random])
#         header = {
#             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
#             "Accept-Encoding": "gzip, deflate, br",
#             "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "Host": "taiwanstay.net.tw",
#             "Pragma": "no-cache",
#             "Upgrade-Insecure-Requests": "1",
#             "User-Agent": random_ua
#         }
#         self._logger.debug("產生的 Fake Header: {}".format(header["User-Agent"]))
#         return header

#     async def _delay_continue(self, min: float, max: float) -> float:
#         """
#         延遲並繼續，為了並免請求的次數之間時間過近，透過給予時間的範圍，隨機生成延遲的時間並於完成等待後繼續執行
#         Args:
#             min (float): 隨機時間最小範圍，單位為秒
#             max (float): 隨機時間最大範圍，單位為秒
#         Returns:
#             float: 回傳生成的等待時間
#         """
#         # 隨機產生在 1 - 2 的福點數時間範圍，並格式化成小數點兩位
#         rand_sec = float("{:.2f}".format(random.uniform(1.5, 2.2)))
#         await asyncio.sleep(rand_sec)
#         return rand_sec

#     async def _check_does_normal_resp(self, resp: SyncHttpResponse) -> bool:
#         if resp.url == self._conf.ABNORMAL_URL:
#             lxmltree = etree.HTML(resp.raw_content)
#             content = etree.tostring(lxmltree, method='html', pretty_print=True).decode('utf-8')
#             raise ReqSysAbnoramlError(resp.status_code, "解析旅館資料異常！皆為 None", resp.url, content)
#         return True

#     @retry(stop=stop_after_attempt(3),
#            wait=wait_fixed(5),
#            retry=retry_if_exception_type(ReqSysAbnoramlError))
#     async def retryable_requests(self,
#                                  url: str,
#                                  params: dict,
#                                  headers: Optional[dict] = None,
#                                  cookies: Optional[dict] = None) -> SyncHttpResponse:
#         try:
#             encoded_params = parse.urlencode(params)
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(url, params=encoded_params, headers=headers, cookies=cookies) as resp:
#                     sync_resp = SyncHttpResponse(await resp.read(),
#                                                  await resp.text(),
#                                                  resp.status,
#                                                  resp.headers,
#                                                  resp.cookies,
#                                                  resp.url.human_repr())
#                     self._logger.debug(f"Response Cookies: {sync_resp.cookies}")
#                     await self._check_does_normal_resp(sync_resp)
#             return sync_resp
#         except ReqSysAbnoramlError as rse:
#             self._logger.error(f" ！ 網站異常 ！ #########################################")
#             self._logger.error(f">> 請求網址: {url}, params: {params}, headers: {headers}, cookies: {cookies}")
#             self._logger.error(f">> 回應網址：{rse.url}, 頁面狀態碼： {rse.http_code}\n" + rse.content)
#             raise rse

#     async def _get_total_page_of_county(self, city: str, county: CountyOption) -> TotalPageOfCounty:
#         """
#         取得指定的縣市與下的特定市區鄉鎮的旅館頁面總頁數
#         Args:
#             city (str): 縣市名
#             county (CountyOption): 市區鄉鎮 DTO
#         Returns:
#             TotalPageOfCounty: 市區鄉鎮的總頁數 DTO
#         """
#         try:
#             self._params["sel_city"] = city
#             self._params["sel_area"] = county.value
#             fake_headers = await self._gen_fake_header()
#             resp: SyncHttpResponse = await self.retryable_requests(self._conf.SEARCH_URL,
#                                                                    self._params,
#                                                                    headers=fake_headers)
#             soup = BeautifulSoup(resp.raw_content, "html.parser")
#             page_with_num = soup.find("span", class_="totalbox")
#             pages = page_with_num.find_all("span")[0].text
#             numbers = page_with_num.find_all("span")[1].text
#             return TotalPageOfCounty(int(pages), (numbers))
#         except Exception as e:
#             self._logger.error(f"取得所有頁數時異常！")
#             raise e

#     async def _get_hotels_of_pages(self, pages: int) -> List[HotelInfo]:
#         """
#         取得該市區鄉鎮的所有頁面下總旅館資料
#         Args:
#             pages (int): 該市區鄉鎮的總頁數
#         Returns:
#             List[HotelInfo]: 該市區鄉鎮的所有旅館資料
#         """
#         try:
#             hotels_class_css = "col-md-12 col-sm-12 nopadding items-container simple-items"
#             hotels_of_pages = []
#             for page in range(1, pages + 1):
#                 self._logger.info(f"#### 開始第 {page} 頁 ################################")
#                 self._params["page"] = page
#                 fake_headers = await self._gen_fake_header()
#                 resp: SyncHttpResponse = await self.retryable_requests(self._conf.SEARCH_URL,
#                                                                        self._params,
#                                                                        headers=fake_headers)
#                 hotels_id: List[int] = self._get_hotels_id_of_current_page(page, resp.raw_content)
#                 hotels = await self._retrieve_hotels_of_current_page(hotels_id)
#                 hotels_of_pages.extend(hotels)
#             return hotels_of_pages
#         except Exception as e:
#             self._logger(f"取得 {page} 頁的所有 Hotels 時異常 ！")
#             raise e

#     def _get_hotels_id_of_current_page(self, page: int, html: bytes) -> List[int]:
#         """
#         取得目前此頁面下顯示的所有旅館 id，作為訪問用
#         Args:
#             html (bytes): 該頁面的 HTML 內容
#         Returns:
#             List[int]: 該頁面的所有旅館 id
#         """
#         try:
#             # 透過 /@href 語法直接取得連結屬性
#             hotel_links_xpath = "//*[@id='searchpage']/div/div/div[3]/div/div/a/@href"
#             hotelstree = etree.HTML(html)
#             hotel_links = hotelstree.xpath(hotel_links_xpath)
#             hotels_id = [link.split("hotel_id=")[1] for link in hotel_links]
#             return hotels_id
#         except Exception as e:
#             self._logger(f"解析第 {page} 頁的所有旅館訪問連結取得 id 時異常 ！")
#             raise e

#     async def _retrieve_hotels_of_current_page(self, hotels_id: List[int]) -> List[HotelInfo]:
#         """
#         透過該頁面下的所有旅館 id 取得旅館資料
#         Args:
#             hotels_id (List[int]): 該頁面的所有旅館 id

#         Returns:
#             List[HotelInfo]: 該頁面的所有旅館資料
#         """
#         hotels = []
#         for index, hotel_id in enumerate(hotels_id):
#             # 隨機產生在 1.5 - 2.2 之間的延遲
#             # delay = self._delay_continue(0.5, 1.5)
#             self._logger.info(f"開始爬取旅館 => 索引：{index}, ID: {hotel_id}")
#             hotel = await self._retrieve_hotel_info_by_id(hotel_id)
#             hotels.append(hotel)
#         return hotels

#     async def _show_hotel(self, hotel: HotelInfo):
#         self._logger.info(f"------------- 完成爬取，旅館資料 -------------------------")
#         self._logger.info(f" - {HotelField.Id.value}: {hotel[HotelField.Id]}")
#         self._logger.info(f" - {HotelField.Name.value}: {hotel[HotelField.Name]}")
#         self._logger.debug(f" - {HotelField.Phone.value}: {hotel[HotelField.Phone]}")
#         self._logger.debug(f" - {HotelField.Address.value}: {hotel[HotelField.Address]}")
#         self._logger.debug(f" - {HotelField.Rooms.value}: {hotel[HotelField.Rooms]}")
#         self._logger.debug(f" - {HotelField.Prices.value}: {hotel[HotelField.Prices]}")
#         self._logger.debug(f" - {HotelField.Email.value}: {hotel[HotelField.Email]}")
#         self._logger.debug(f" - {HotelField.Url.value}: {hotel[HotelField.Url]} \n")

#     async def _retrieve_hotel_info_by_id(self, hotel_id: int) -> HotelInfo:
#         """
#         透過訪問旅館資料的 id 取得該旅館頁面下的旅館相關資訊
#         Args:
#             hotel_id (int): 旅館 id
#         Returns:
#             HotelInfo: 該旅館資料
#         """
#         try:
#             params = {"hotel_id": hotel_id}
#             fake_headers = await self._gen_fake_header()
#             resp: SyncHttpResponse = await self.retryable_requests(self._conf.HOTEL_PAGE_URL,
#                                                                    params,
#                                                                    headers=fake_headers)
#             parsed = {}
#             parsing_xpath = {
#                 HotelField.Name: "//*[@id='right-hotel']/h2/text()",
#                 HotelField.Address: "//*[@id='right-hotel']/div[4]/div[2]/p/span[2]/text()",
#                 HotelField.Phone: "//*[@id='tel_div']/p/span[2]/text()",
#                 HotelField.Email: "//*[@id='email_div']/a/p/span[2]/text()",
#                 HotelField.Rooms: "//*[@id='right-hotel']/div[5]/div[2]/p/span[2]/text()",
#                 HotelField.Prices: "//*[@id='right-hotel']/div[5]/div[3]/p/span[2]/text()",
#                 HotelField.Url: "//*[@id='website_div']/p/span[2]/a"
#             }
#             retreived_func = {
#                 HotelField.Name: lambda elems: elems[0] if elems else None,
#                 HotelField.Address: lambda elems: elems[0] if elems else None,
#                 HotelField.Phone: lambda elems: elems[0] if elems else None,
#                 HotelField.Email: lambda elems: elems[0] if elems else None,
#                 HotelField.Rooms: lambda elems: elems[0] if elems else None,
#                 HotelField.Prices: lambda elems: elems[0] if elems else None,
#                 HotelField.Url: lambda elems: elems[0].get("href") if elems and elems[0].get("href") else None
#             }
#             hoteltree = etree.HTML(resp.raw_content)
#             for field, xpath in parsing_xpath.items():
#                 parsed[field] = retreived_func[field](hoteltree.xpath(xpath))

#             hotel = {
#                 HotelField.Id: str(hotel_id),
#                 HotelField.Name: parsed[HotelField.Name],
#                 HotelField.Phone: parsed[HotelField.Phone],
#                 HotelField.Address: parsed[HotelField.Address],
#                 HotelField.Rooms: parsed[HotelField.Rooms],
#                 HotelField.Prices: parsed[HotelField.Phone],
#                 HotelField.Email: parsed[HotelField.Email],
#                 HotelField.Url: parsed[HotelField.Url],
#             }
#             await self._show_hotel(hotel)
#             return hotel
#         except Exception as e:
#             self._logger.error(f"解析旅館 {hotel_id} 的資訊頁面異常！")
#             raise e

#     async def _store_excel(self, county_name: str, hotels: List[HotelInfo], excel: ExcelStore):
#         try:
#             # 新增此市區鄉鎮的 Sheet
#             sheet = excel.add_sheet(county_name, self._conf.PARSED_COLUMNS)
#             self._logger.info(f"寫入 {county_name} 資料至 Excel ....")
#             # 抓出每一的鄉鎮的所有頁面資料
#             for idx, hotel in enumerate(hotels):
#                 # 第 0 列為 Header，所以 idx 需要 + 1
#                 excel.store_hotel(sheet, idx + 1, self._conf.PARSED_COLUMNS, hotel)
#             self._logger.info(f"#### 完成寫入 {county_name} 的旅館資料 ... !")
#         except Exception as e:
#             self._logger.error(" ！ 寫入 Excel 異常 ！ ")
#             raise e

#     async def _get_hotels_of_county(self, city: str, county: CountyOption) -> List[HotelInfo]:
#         total: TotalPageOfCounty = await self._get_total_page_of_county(city, county)
#         self._logger.info(f"==== 開始抓取城市: {city} {county.name}, 共有 {total.pages} 頁，{total.num_of_hotels} 筆 ====")
#         hotels_of_county: List[HotelInfo] = await self._get_hotels_of_pages(total.pages)
#         return hotels_of_county

#     async def _retrieve_counties_hotels(self,
#                                         city: str,
#                                         counties: List[CountyOption],
#                                         excel: ExcelStore) -> ExcelStore:
#         for county in counties:
#             hotels_of_county = await self._get_hotels_of_county(city, county)
#             await self._store_excel(county.name, hotels_of_county, excel)
#         return excel

#     def parsing(self, excel: ExcelStore) -> ExcelStore:
#         # 先對每一個城市爬蟲個鄉鎮
#         try:
#             city = self._conf.CITIES_CODE[self._selected_code]
#             counties: List[CountyOption] = self.find_counties(city)
#             coroutine = self._retrieve_counties_hotels(city, counties, excel)
#             excel = asyncio.run(coroutine)
#             return excel
#         except Exception as e:
#             raise e
#         finally:
#             excel.close()
