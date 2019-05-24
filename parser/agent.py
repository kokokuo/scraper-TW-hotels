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
from .dto import CountyOption, TotalPageOfCounty
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
            "Cookie": "OAKS_SESS1=l7ginifqoe58sccvof9n3qec64",
            "Host": "taiwanstay.net.tw",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": fake_ua.chrome
        }
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

    def _get_hotels_of_pages(self, pages: int) -> None:
        hotels_class_css = "col-md-12 col-sm-12 nopadding items-container simple-items"
        for page in range(1, pages):
            print(f"#### 開始第 {page} 頁 ####")
            self._payload["page"] = page
            resp = requests.get(self.WEBSITE_URL + self.SEARCH_ROUNTE,
                                params=self._payload,
                                headers=self._gen_header())
            soup = BeautifulSoup(resp.content, "html.parser")
            div_of_hotels = soup.find("div", class_=hotels_class_css)
            elem_of_hotels = div_of_hotels.find_all("div", class_="item")
            for hotel in elem_of_hotels:
                # 取得 Hotel 連結的後半段 hotel_id, e.g: ./hotel_content.php?hotel_id=2894
                hotel_id = hotel.find("a").attrs["href"].split("hotel_id=")[1]
                print(hotel_id)
        return None

    def _get_hotel_info(self, hotel_id: int) -> None:
        payload = {"hotel_id": hotel_id}
        resp = requests.get(self.WEBSITE_URL + self.HOTEL_PAGE_ROUTE,
                            params=payload,
                            headers=self._gen_header())

    def start_parsing(self) -> Workbook:
        # 先對每一個城市爬蟲個鄉鎮
        city = self.CITIES_CODE[self._selected_code]

        counties: List[CountyOption] = self._get_selected_city_counties(city)
        for county in counties:
            html_content = self._get_html_content_of_county(city, county)
            total: TotalPageOfCounty = self._get_total_page_of_county(html_content)
            print(f"==== 開始抓取城市: {city} {county.name}, 共有 {total.pages} 頁，{total.num_of_hotels} 筆 ====")
            self._get_hotels_of_pages(total.pages)
        # county_list = self._parse_county(self.WEBSITE_URL, self._selected_code)
        # for county in county_list:
        #     print("======", county.code, county.text, "======")
        #     self._payload["hotelCounty"] = county.code
        #     # 回到第一頁
        #     self._payload["page"] = 1
        #     hotels_info = self._parse_each_page_hotels(self.WEBSITE_URL, self._payload)
        #     # 寫入 XLS
        #     worksheet = self._workbook.add_worksheet(county.text)
        #     # 定義標題的數量
        #     worksheet.set_column(0, len(self.REQ_COLUMNS) - 1, 20)
        #     # 定義格式
        #     cell_format = self._workbook.add_format({"bold": True, "bg_color": "#D8F6CE", "font_size": 14})
        #     content_format = self._workbook.add_format({"font_size": 12})
        #     link_format = self._workbook.add_format({"color": "blue", "underline": 1, "font_size": 12})
        #     # 寫入第一列標題
        #     worksheet.write_row("A1", self.REQ_COLUMNS, cell_format)
        #     # 抓出每一的鄉鎮的所有頁面資料
        #     for index, elem in enumerate(hotels_info):
        #         hotel_row = (
        #             elem[u"旅宿民稱"] if u"旅宿民稱" in elem else "",
        #             elem[u"地址"] if u"地址" in elem else "",
        #             elem[u"訂房專線"] if u"訂房專線" in elem else "",
        #             "",
        #             elem[u"電子信箱"] if u"電子信箱" in elem else "",
        #             "",
        #             elem[u"定價"] if u"定價" in elem else "",
        #         )
        #         hotel_link = elem[u"網址"] if u"網址" in elem else ""
        #         room_num = int(elem[u"總房間數"]) if u"總房間數" in elem else 0
        #         # 調整 URL
        #         pattern = "^http[s]://"
        #         # 如果沒有包含，則加工
        #         if hotel_link and re.search(pattern, hotel_link) is None:
        #             hotel_link = "http://" + hotel_link
        #         worksheet.write_row(index + 1, 0, hotel_row, content_format)
        #         # 用數值格式，寫入房間數
        #         worksheet.write_number(index + 1, 5, room_num, content_format)
        #         # 另外採用網址形式
        #         worksheet.write_url(index + 1, 3, hotel_link, link_format)
        self._workbook.close()
        return self._workbook

    # def _parse_each_hotel_detail(self, link):
    #     """
    #     對每一個 hotel 的頁面連結做解析
    #     Args:
    #         link: 每一個 hotel 的頁面連結
    #     """
    #     hotel_data = {}
    #     resp = requests.get(link)
    #     soup = BeautifulSoup(resp.content, "html.parser")
    #     hotel_name = soup.find("h3", class_="ct-title").span.text
    #     hotel_infos = soup.find("ul", class_="grayListDot").find_all("li", class_="listItem")
    #     print("旅宿民稱 ", hotel_name.strip())
    #     for info in hotel_infos:
    #         title = info.p.text.strip()
    #         content = info.span.text.strip()
    #         if info.p.text.strip() in self.REQ_COLUMNS:
    #             print(title, content)
    #             hotel_data[title] = content
    #     hotel_data[u"旅宿民稱"] = hotel_name
    #     return hotel_data

    # def _parse_each_page_hotels(self, root_url, payload):
    #     """
    #     找出第一頁的爬蟲網頁後，並找數共有多少 option 頁面，對每夜去分別做解析
    #     """
    #     resp = requests.get(root_url + "/Home/Search", params=payload)
    #     # utf-8 格式
    #     # print resp.encoding
    #     soup = BeautifulSoup(resp.content, "html.parser")
    #     # prettify 格式化可以印出中文
    #     # print(soup.prettify())

    #     page = soup.find("div", class_="jumppage")
    #     if page is None or page == "":
    #         print("查無資料.....")
    #         return []

    #     options = page.find("select", {"name": "page"}).find_all("option")
    #     hotels_info = []
    #     for option in options:
    #         print("第", option.text, "頁 === >")
    #         # 尋找每一頁的旅店資料以及 Detail 連結
    #         payload["page"] = int(option.text)
    #         resp = requests.get(root_url + "/Home/Search", params=payload)
    #         soup = BeautifulSoup(resp.content, "html.parser")

    #         for hotel in soup.find_all("li", class_="listitem"):
    #             sub_link_url = hotel.find("a").get("href")
    #             detail_link = root_url + sub_link_url
    #             print("此旅館民宿的 URL Link = {link}".fomat(detail_link))
    #             #  在呼叫進入每一個頁面爬資料
    #             data = self._parse_each_hotel_detail(detail_link)
    #             print("")
    #             hotels_info.append(data)
    #     return hotels_info

    # def _parse_county(self, root_url, city_code) -> List:
    #     """
    #     找出此城市所有鄉鎮
    #     Args:
    #         city_code: 城市的代碼 e.g 新北市為F, 台南市為R
    #     Returns:
    #         County of List
    #     """
    #     # 找出所有鄉鎮
    #     county_resp = requests.post(root_url + "/Home/GetCounty", data={"city": city_code})
    #     county_soup = BeautifulSoup(county_resp.content, "html.parser")
    #     # print county_soup.prettify()
    #     county_options = county_soup.find_all("option")
    #     return [
    #         County(code=option["value"], text=option.text.strip())
    #         for option in county_options if option["value"] != ""
    #     ]
