# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import xlsxwriter
import config
from config import County
import re

req_columns = [u"旅宿民稱", u"地址", u"訂房專線", u"網址", u"電子信箱", u"總房間數", u"定價"]


def parse_each_hotel_detail(link):
    """
    對每一個 hotel 的頁面連結做解析
    Args:
        link: 每一個 hotel 的頁面連結
    """
    hotel_data = {}
    resp = requests.get(link)
    soup = BeautifulSoup(resp.content, "html.parser")
    hotel_name = soup.find("h3", class_="ct-title").span.text
    hotel_infos = soup.find("ul", class_="grayListDot").find_all("li", class_="listItem")
    print("旅宿民稱 ", hotel_name.strip())
    for info in hotel_infos:
        title = info.p.text.strip()
        content = info.span.text.strip()
        if info.p.text.strip() in req_columns:
            print(title, content)
            hotel_data[title] = content
    hotel_data[u"旅宿民稱"] = hotel_name
    return hotel_data


def parse_each_page_hotels(root_url, payload):
    """
    找出第一頁的爬蟲網頁後，並找數共有多少 option 頁面，對每夜去分別做解析
    """
    resp = requests.get(root_url + "/Home/Search", params=payload)
    # utf-8 格式
    # print resp.encoding
    soup = BeautifulSoup(resp.content, "html.parser")
    # prettify 格式化可以印出中文
    # print(soup.prettify())

    page = soup.find("div", class_="jumppage")
    if page is None or page == "":
        print("查無資料.....")
        return []

    options = page.find("select", {"name": "page"}).find_all("option")
    hotels_info = []
    for option in options:
        print("第", option.text, "頁 === >")
        # 尋找每一頁的旅店資料以及 Detail 連結
        payload["page"] = int(option.text)
        resp = requests.get(root_url + "/Home/Search", params=payload)
        soup = BeautifulSoup(resp.content, "html.parser")

        for hotel in soup.find_all("li", class_="listitem"):
            sub_link_url = hotel.find("a").get("href")
            detail_link = root_url + sub_link_url
            print("此旅館民宿的 URL Link = {link}".fomat(detail_link))
            #  在呼叫進入每一個頁面爬資料
            data = parse_each_hotel_detail(detail_link)
            print("")
            hotels_info.append(data)
    return hotels_info


def parse_county(root_url, city_code):
    """
    找出此城市所有鄉鎮
    Args:
        city_code: 城市的代碼 e.g 新北市為F, 台南市為R
    Returns:
        County of List
    """
    # 找出所有鄉鎮
    county_resp = requests.post(root_url + "/Home/GetCounty", data={"city": city_code})
    county_soup = BeautifulSoup(county_resp.content, "html.parser")
    # print county_soup.prettify()
    county_options = county_soup.find_all("option")
    return [
        County(code=option["value"], text=option.text.strip())
        for option in county_options if option["value"] != ""
    ]


def main():
    # hotelCity = R 是台南市的身分證字號字首，例如新北市要填入 F
    # ver1.
    # Search url
    # req_data = {
    #     "hotelCity":"R", "hotelType": None, "hotelCounty": None, "starLevel": None,
    #     "host": False, "salePrice": None, "roomAmount": None, "roomType": None, "languageType": None,
    #     "certified": None, "conference": False, "accessible":False, "keyword": None
    # }
    # resp = requests.post(root_url + "/Home/Search", data=req_data)

    # ver2.
    # 在查詢分頁時，偶然發現可以 get
    # http://taiwanstay.net.tw/Home/Search?hotelCity=R&conference=False&accessible=False&accessibility=False&roompricelow=False&host=False&page=7&listPage=10&corder=

    taiwan_cities_code = {
        "F": "新北市", "A": "臺北市", "H": "桃園市", "B": "臺中市", "R": "臺南市",
        "S": "高雄市", "G": "宜蘭縣", "J": "新竹縣", "K": "苗栗縣", "N": "彰化縣",
        "M": "南投縣", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "V": "臺東縣",
        "U": "花蓮縣", "X": "澎湖縣", "C": "基隆市", "O": "新竹市", "I": "嘉義市",
        "W": "金門縣", "Z": "連江縣"
    }
    print("寫選擇要抓取的資料: ")
    for city_code in taiwan_cities_code.keys():
        print("縣市: {}, 輸入的代碼: {}".format(taiwan_cities_code[city_code], city_code))
    city_code = input("請輸入代碼 (大寫) >> ").upper()
    if city_code not in taiwan_cities_code.keys():
        print("不存在此代碼...請重新執行")
        exit()

    # 保存要抓取的縣市 xlsx 名稱
    workbook = xlsxwriter.Workbook(taiwan_cities_code[city_code] + "所有旅宿統計資料.xlsx")
    payload = config.PAYLOAD
    # 先對每一個城市爬蟲個鄉鎮
    payload["hotelCity"] = city_code
    county_list = parse_county(config.ROOT_URL, city_code)
    for county in county_list:
        print("======", county.code, county.text, "======")
        payload["hotelCounty"] = county.code
        # 回到第一頁
        payload["page"] = 1
        hotels_info = parse_each_page_hotels(config.ROOT_URL, payload)
        # 寫入 XLS
        worksheet = workbook.add_worksheet(county.text)
        # 定義標題的數量
        worksheet.set_column(0, len(req_columns) - 1, 20)
        # 定義格式
        cell_format = workbook.add_format({"bold": True, "bg_color": "#D8F6CE", "font_size": 14})
        content_format = workbook.add_format({"font_size": 12})
        link_format = workbook.add_format({"color": "blue", "underline": 1, "font_size": 12})
        # 寫入第一列標題
        worksheet.write_row("A1", req_columns, cell_format)
        # 抓出每一的鄉鎮的所有頁面資料
        for index, elem in enumerate(hotels_info):
            hotel_row = (
                elem[u"旅宿民稱"] if u"旅宿民稱" in elem else "",
                elem[u"地址"] if u"地址" in elem else "",
                elem[u"訂房專線"] if u"訂房專線" in elem else "",
                "",
                elem[u"電子信箱"] if u"電子信箱" in elem else "",
                "",
                elem[u"定價"] if u"定價" in elem else "",
            )
            hotel_link = elem[u"網址"] if u"網址" in elem else ""
            room_num = int(elem[u"總房間數"]) if u"總房間數" in elem else 0
            # 調整 URL
            pattern = "^http[s]://"
            # 如果沒有包含，則加工
            if hotel_link and re.search(pattern, hotel_link) is None:
                hotel_link = "http://" + hotel_link
            worksheet.write_row(index + 1, 0, hotel_row, content_format)
            # 用數值格式，寫入房間數
            worksheet.write_number(index + 1, 5, room_num, content_format)
            # 另外採用網址形式
            worksheet.write_url(index + 1, 3, hotel_link, link_format)
    workbook.close()


if __name__ == "__main__":
    main()
