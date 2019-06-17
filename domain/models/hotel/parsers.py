from copy import deepcopy
from typing import List, Dict
from logging import Logger
from lxml import etree
from bs4 import BeautifulSoup
from domain.models.hotel.field import HotelField
from domain.models.region.county import CountyVO
from domain.models.hotel.pages import PagesOfHotelVO
from domain.models.hotel.content import HotelContentVO
from infra.asynchttp.resp import SyncHttpResponse
from infra.asynchttp.header import FakeHeaderGenerator
from infra.asynchttp.requester import RetryableRequester
from infra.asynchttp import fake_header_generator, retryable_requester
from infra.logging import scraping_logger
from settings.config import Config


class PagesOfCountyParser(object):
    """
    該市區鄉鎮的旅館頁數解析器
    """
    def __init__(self,
                 url: str,
                 params: dict,
                 scraping_logger: Logger,
                 fake_header_generator: FakeHeaderGenerator,
                 retryable_requester: RetryableRequester) -> None:
        self._url = url
        self._params = params
        self._logger = scraping_logger
        self._fake_header = fake_header_generator
        self._requester = retryable_requester

    async def extract(self, city_name: str, county: CountyVO) -> PagesOfHotelVO:
        try:
            self._params["sel_city"] = city_name
            self._params["sel_area"] = county.value
            fake_headers = await self._fake_header.generate()
            resp: SyncHttpResponse = await self._requester.get(self._url,
                                                               self._params,
                                                               headers=fake_headers)
            soup = BeautifulSoup(resp.raw_content, "html.parser")
            page_with_num = soup.find("span", class_="totalbox")
            pages = page_with_num.find_all("span")[0].text
            numbers = page_with_num.find_all("span")[1].text
            self._logger.info(f"{city_name} {county.name}, 共有 {pages} 頁，{numbers} 筆")
            return PagesOfHotelVO(int(pages), (numbers))
        except Exception as e:
            self._logger.error(f" [ ERROR ]    取得所有頁數時異常 ！")
            raise e


class HotelsOfCountyParser(object):
    """
    市區鄉鎮下的所有旅館解析器
    """
    def __init__(self,
                 url: str,
                 params: dict,
                 hotel_href_xpath: str,
                 scraping_logger: Logger,
                 fake_header_generator: FakeHeaderGenerator,
                 retryable_requester: RetryableRequester) -> None:
        self._url = url
        self._params = params
        self._hotel_href_xpath = hotel_href_xpath
        self._logger = scraping_logger
        self._fake_header = fake_header_generator
        self._requester = retryable_requester

    def _extract_hotels_id(self, page: int, html: bytes) -> List[int]:
        try:
            # 透過 /@href 語法直接取得連結屬性
            hotel_links_xpath = self._hotel_href_xpath
            hotelstree = etree.HTML(html)
            hotel_links = hotelstree.xpath(hotel_links_xpath)
            hotels_id = [link.split("hotel_id=")[1] for link in hotel_links]
            return hotels_id
        except Exception as e:
            self._logger.error(f" [ ERROR ]    解析第 {page} 頁的所有旅館訪問連結取得 id 時異常 ！")
            raise e

    async def _extract_hotels(self, hotels_id: List[int]) -> List[HotelContentVO]:
        """
        透過該頁面下的所有旅館 id 取得旅館資料
        Args:
            hotels_id (List[int]): 該頁面的所有旅館 id

        Returns:
            List[HotelContentVO]: 該頁面的所有旅館資料
        """
        hotels: List[HotelContentVO] = []
        hotel_content_parser = HotelContentVOParser(Config.HOTEL_CONTENT_URL,
                                                    Config.HOTEL_CONTENT_XPATH,
                                                    scraping_logger,
                                                    fake_header_generator,
                                                    retryable_requester)
        for index, hotel_id in enumerate(hotels_id):
            # 隨機產生在 1.5 - 2.2 之間的延遲 -> delay = self._delay_continue(0.5, 1.5)
            self._logger.info(f"開始爬取旅館 => 索引：{index}, ID: {hotel_id}")
            hotel: HotelContentVO = await hotel_content_parser.extract(hotel_id)
            hotels.append(hotel)
        return hotels

    async def extract_all(self, city_name: str, county: CountyVO, pages: PagesOfHotelVO):
        """
        取得該市區鄉鎮的所有頁面下總旅館資料
        Args:
            pages (int): 該市區鄉鎮的總頁數
        Returns:
            List[HotelContentVO]: 該市區鄉鎮的所有旅館資料
        """
        try:
            hotels_of_pages = []
            self._params["sel_city"] = city_name
            self._params["sel_area"] = county.value
            for page in range(1, pages.total + 1):
                self._logger.info(f" [ Next Page ]    第 {page} 頁 =====================")
                self._params["page"] = page
                fake_headers = await self._fake_header.generate()
                resp: SyncHttpResponse = await self._requester.get(self._url,
                                                                   self._params,
                                                                   headers=fake_headers)
                hotels_id: List[int] = self._extract_hotels_id(page, resp.raw_content)
                hotels = await self._extract_hotels(hotels_id)
                hotels_of_pages.extend(hotels)
            return hotels_of_pages
        except Exception as e:
            self._logger.error(f" [ ERROR ]    取得 {page} 頁的所有 Hotels 時異常 ！ ")
            raise e


class HotelContentVOParser(object):
    """
    旅館資訊內容頁解析器
    """
    def __init__(self,
                 url: str,
                 hotel_content_xpath: Dict[HotelField, str],
                 scraping_logger: Logger,
                 fake_header_generator: FakeHeaderGenerator,
                 retryable_requester: RetryableRequester) -> None:
        self._url = url
        self._hotel_content_xpath = hotel_content_xpath
        self._logger = scraping_logger
        self._fake_header = fake_header_generator
        self._requester = retryable_requester

    async def _logging(self, hotel: HotelContentVO):
        self._logger.info(f" [ OK ]    旅館內容爬取完成 =============")
        self._logger.info(f" [ 旅館 ID  ] : {hotel.id}")
        self._logger.info(f" [ 旅宿民稱 ] : {hotel.name}")
        self._logger.info(f" [ 地址     ] : {hotel.address}")
        self._logger.info(f" [ 訂房專線 ] : {hotel.phone}")
        self._logger.info(f" [ 網址     ] : {hotel.url}")
        self._logger.info(f" [ 電子信箱 ] : {hotel.email}")
        self._logger.info(f" [ 總房間數 ] : {hotel.rooms}")
        self._logger.info(f" [ 定價     ] : {hotel.prices}")
        self._logger.info(f" =======================================")

    async def extract(self, hotel_id: int) -> HotelContentVO:
        """
        透過訪問旅館資料的 id 取得該旅館頁面下的旅館相關資訊
        Args:
            hotel_id (int): 旅館 id
        Returns:
            HotelContentVO: 該旅館資料
        """
        try:
            self._params = {"hotel_id": hotel_id}
            fake_headers = await self._fake_header.generate()
            resp: SyncHttpResponse = await self._requester.get(self._url,
                                                               self._params,
                                                               headers=fake_headers)
            parsed = {}
            retreived_func = {
                HotelField.Name: lambda elems: elems[0] if elems else None,
                HotelField.Address: lambda elems: elems[0] if elems else None,
                HotelField.Phone: lambda elems: elems[0] if elems else None,
                HotelField.Email: lambda elems: elems[0] if elems else None,
                HotelField.Rooms: lambda elems: elems[0] if elems else None,
                HotelField.Prices: lambda elems: elems[0] if elems else None,
                HotelField.Url: lambda elems: elems[0].get("href") if elems and elems[0].get("href") else None
            }
            hoteltree = etree.HTML(resp.raw_content)
            for field, xpath in self._hotel_content_xpath.items():
                parsed[field] = retreived_func[field](hoteltree.xpath(xpath))

            hotel = HotelContentVO(hotel_id,
                                   parsed[HotelField.Name],
                                   parsed[HotelField.Phone],
                                   parsed[HotelField.Address],
                                   parsed[HotelField.Rooms],
                                   parsed[HotelField.Prices],
                                   parsed[HotelField.Email],
                                   parsed[HotelField.Url])
            await self._logging(hotel)
            return hotel
        except Exception as e:
            self._logger.error(f" [ ERROR ]    解析旅館 {hotel_id} 的資訊頁面異常 ！")
            raise e


pages_parser = PagesOfCountyParser(Config.SEARCH_URL,
                                   Config.HOTELS_COMMON_SERACH_PARAMS,
                                   scraping_logger,
                                   fake_header_generator,
                                   retryable_requester)

hotels_of_county_parser = HotelsOfCountyParser(Config.SEARCH_URL,
                                               Config.HOTELS_COMMON_SERACH_PARAMS,
                                               Config.HOTEL_HREF_XPATH,
                                               scraping_logger,
                                               fake_header_generator,
                                               retryable_requester)
