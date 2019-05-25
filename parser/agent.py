# -*- coding: utf-8 -*-
import re
import logging
from typing import List, Dict
import requests
from lxml import etree
from bs4 import BeautifulSoup
from xlsxwriter import Workbook
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from .dto import CountyOption, TotalPageOfCounty, HotelInfo
from config import County


class TaiwanHotelParserAgent(object):
    REQ_COLUMNS = [u"旅宿民稱", u"地址", u"訂房專線", u"網址", u"電子信箱", u"總房間數", u"定價"]
    WEBSITE_URL = "https://taiwanstay.net.tw"
    SEARCH_ROUNTE = "/tourism_web/search.php"
    HOTEL_PAGE_ROUTE = "/tourism_web/hotel_content.php"
    CITIES_CODE = {
        "F": "新北市", "A": "臺北市", "H": "桃園市", "B": "臺中市", "R": "臺南市",
        "S": "高雄市", "G": "宜蘭縣", "J": "新竹縣", "K": "苗栗縣", "N": "彰化縣",
        "M": "南投縣", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "V": "臺東縣",
        "U": "花蓮縣", "X": "澎湖縣", "C": "基隆市", "O": "新竹市", "I": "嘉義市",
        "W": "金門縣", "Z": "連江縣"
    }

    def __init__(self, selected_code: str, workbook: Workbook) -> None:
        self._selected_code: str = selected_code
        self._payload: dict = {
            "page": 1,
            "sortBy": None,
            "act": None,
            "sel_hotel[]": [1, 2, 3],
            "sel_keyword": None,
            "sel_city": None,
            "sel_keyword": None,
            "sel_city": None,
            "sel_area": None,
            "sel_price": None,
            "sel_room_num": None,
            "sel_type": None,
        }
        self._workbook: Workbook = workbook

    def _get_selected_city_counties(self, city_name: str) -> List[CountyOption]:
        """
        藉由 Selenium 模擬點擊縣市，取得指定縣市的所有省區資料
        Returns:
            List[CountyOption]: 此城市的所有省區
        """
        options = webdriver.ChromeOptions()
        # 不開啟 Browser 的 GUI
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(self.WEBSITE_URL)
        selector: Select = Select(driver.find_element_by_xpath("//*[@id='sel_city']"))
        selector.select_by_value(city_name)
        counties_options = driver.find_elements_by_xpath("//*[@id='sel_area']/option")
        counties: List[CountyOption] = [
            CountyOption(option.text, option.get_attribute("value"))
            for option in counties_options if option.get_attribute("value")
        ]
        return counties

    def _gen_header(self):
        fake_ua = UserAgent()
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "taiwanstay.net.tw",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": fake_ua.chrome
        }
        # "Cookie": "OAKS_SESS1=l7ginifqoe58sccvof9n3qec64",
        return header

    def _get_total_page_of_county(self, html: bytes) -> TotalPageOfCounty:
        soup = BeautifulSoup(html, "html.parser")
        page_with_num = soup.find("span", class_="totalbox")
        pages = page_with_num.find_all("span")[0].text
        numbers = page_with_num.find_all("span")[1].text
        return TotalPageOfCounty(int(pages), (numbers))

    def _get_html_content_of_county(self, city: str, county: CountyOption) -> bytes:
        self._payload["sel_city"] = city
        self._payload["sel_area"] = county.value
        resp = requests.get(self.WEBSITE_URL + self.SEARCH_ROUNTE, 
                            params=self._payload,
                            headers=self._gen_header())
        return resp.content

    def _get_hotels_of_pages(self, pages: int) -> List[HotelInfo]:
        hotels_class_css = "col-md-12 col-sm-12 nopadding items-container simple-items"
        hotels_of_pages = []
        for page in range(1, pages + 1):
            print(f"#### 開始第 {page} 頁 ################################")
            self._payload["page"] = page
            resp = requests.get(self.WEBSITE_URL + self.SEARCH_ROUNTE,
                                params=self._payload,
                                headers=self._gen_header())
            hotels_id: List[int] = self._get_hotels_id_of_current_page(resp.content)
            hotels = self._retrieve_hotels_of_current_page(hotels_id)
            hotels_of_pages.extend(hotels)
        return hotels_of_pages

    def _get_hotels_id_of_current_page(self, html_content: bytes) -> List[int]:
        hotelstree = etree.HTML(html_content)
        # 透過 /@href 語法直接取得連結屬性
        hotel_links = hotelstree.xpath("//*[@id='searchpage']/div/div/div[3]/div/div/a/@href")
        hotels_id = [link.split("hotel_id=")[1] for link in hotel_links]
        return hotels_id

    def _retrieve_hotels_of_current_page(self, hotels_id: List[int]) -> List[HotelInfo]:
        hotels = []
        for hotel_id in hotels_id:
            hotel = self._retrieve_hotel_info_by_id(hotel_id)
            hotels.append(hotel)
        return hotels

    def _retrieve_hotel_info_by_id(self, hotel_id: int) -> HotelInfo:
        payload = {"hotel_id": hotel_id}
        resp = requests.get(self.WEBSITE_URL + self.HOTEL_PAGE_ROUTE,
                            params=payload,
                            headers=self._gen_header())
        hoteltree = etree.HTML(resp.content)
        # 旅館名稱
        name_elem = hoteltree.xpath("//*[@id='right-hotel']/h2/text()")
        name = name_elem[0] if name_elem else None
        # 訂房專線
        phone_elem = hoteltree.xpath("//*[@id='tel_div']/p/span[2]/text()")
        phone = phone_elem[0] if phone_elem else None
        # 旅館地址
        address_elem = hoteltree.xpath("//*[@id='right-hotel']/div[4]/div[2]/p/span[2]/text()")
        address = address_elem[0] if address_elem else None
        # 房間總數
        room_elem = hoteltree.xpath("//*[@id='right-hotel']/div[5]/div[2]/p/span[2]/text()")
        room = room_elem[0] if room_elem else None
        # 定價
        prices_elem = hoteltree.xpath("//*[@id='right-hotel']/div[5]/div[3]/p/span[2]/text()")
        prices = prices_elem[0] if prices_elem else None
        # 連絡信箱
        email_elem = hoteltree.xpath("//*[@id='email_div']/a/p/span[2]/text()")
        email = email_elem[0] if email_elem else None
        # 網站連結
        siteurl_elem = hoteltree.xpath("//*[@id='website_div']/p/span[2]/a")
        siteurl = siteurl_elem[0].get("href") if siteurl_elem and siteurl_elem[0].get("href") else None

        hotel = HotelInfo(hotel_id, name, phone, address, room, prices, email, siteurl)
        print(f"--------------------------------------")
        print("旅館資料 :")
        print(f" - id: {hotel_id}")
        print(f" - 名稱: {name}")
        print(f" - 訂房電話： {phone}")
        print(f" - 地址: {address}")
        print(f" - 總房間數: {room}")
        print(f" - 定價: {prices}")
        print(f" - 連絡信箱: {email}")
        print(f" - 網站連結: {siteurl} \n")
        return hotel

    def _save_workbook(self, county_name: str, hotels_info: List[HotelInfo]):
        # 寫入 XLS
        worksheet = self._workbook.add_worksheet(county_name)
        # 定義標題的數量
        worksheet.set_column(0, len(self.REQ_COLUMNS) - 1, 20)
        # 定義格式
        cell_format = self._workbook.add_format({"bold": True, "bg_color": "#D8F6CE", "font_size": 14})
        content_format = self._workbook.add_format({"font_size": 12})
        link_format = self._workbook.add_format({"color": "blue", "underline": 1, "font_size": 12})
        # 寫入第一列標題
        worksheet.write_row("A1", self.REQ_COLUMNS, cell_format)
        # 抓出每一的鄉鎮的所有頁面資料
        for index, hotel_info in enumerate(hotels_info):
            hotel_row = (
                hotel_info.name if hotel_info.name else "",
                hotel_info.address if hotel_info.address else "",
                hotel_info.phone if hotel_info.phone else "",
                "",
                hotel_info.email if hotel_info.email else "",
                "",
                hotel_info.prices if hotel_info.prices else ""
            )
            siteurl = hotel_info.siteurl if hotel_info.siteurl else ""
            room = int(hotel_info.room) if hotel_info.room else 0
            # 調整 URL
            pattern = "^http[s]://"
            # 如果沒有包含，則加工
            if siteurl and re.search(pattern, siteurl) is None:
                siteurl = "http://" + siteurl
            worksheet.write_row(index + 1, 0, hotel_row, content_format)
            # 用數值格式，寫入房間數
            worksheet.write_number(index + 1, 5, room, content_format)
            # 另外採用網址形式
            worksheet.write_url(index + 1, 3, siteurl, link_format)

    def start_parsing(self) -> Workbook:
        # 先對每一個城市爬蟲個鄉鎮
        city = self.CITIES_CODE[self._selected_code]

        counties: List[CountyOption] = self._get_selected_city_counties(city)
        for county in counties:
            html_content = self._get_html_content_of_county(city, county)
            total: TotalPageOfCounty = self._get_total_page_of_county(html_content)
            print(f"==== 開始抓取城市: {city} {county.name}, 共有 {total.pages} 頁，{total.num_of_hotels} 筆 ====")
            hotels_of_county: List[HotelInfo] = self._get_hotels_of_pages(total.pages)
            print(f"寫入 {county.name} 資料....")
            self._save_workbook(county.name, hotels_of_county)
        self._workbook.close()
        return self._workbook
