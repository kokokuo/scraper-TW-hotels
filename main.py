# -*- coding: utf-8 -*-
import xlsxwriter
from parser.agent import TaiwanHotelParserAgent


def main():
    taiwan_cities_code = {
        "F": "新北市", "A": "臺北市", "H": "桃園市", "B": "臺中市", "R": "臺南市",
        "S": "高雄市", "G": "宜蘭縣", "J": "新竹縣", "K": "苗栗縣", "N": "彰化縣",
        "M": "南投縣", "P": "雲林縣", "Q": "嘉義縣", "T": "屏東縣", "V": "臺東縣",
        "U": "花蓮縣", "X": "澎湖縣", "C": "基隆市", "O": "新竹市", "I": "嘉義市",
        "W": "金門縣", "Z": "連江縣"
    }

    print("寫選擇要抓取的資料: ")
    cities_code = TaiwanHotelParserAgent.CITIES_CODE
    for city_code in cities_code.keys():
        print("縣市: {}, 輸入的代碼: {}".format(cities_code[city_code], city_code))
    city_code = input("請輸入代碼 (大寫) >> ").upper()
    if city_code not in cities_code.keys():
        print("不存在此代碼，請重新執行！")
        exit()

    # 保存要抓取的縣市 xlsx 名稱
    workbook = xlsxwriter.Workbook(taiwan_cities_code[city_code] + "所有旅宿統計資料.xlsx")
    hotel_parser = TaiwanHotelParserAgent(city_code, workbook)
    hotel_parser.start_parsing()


if __name__ == "__main__":
    main()
