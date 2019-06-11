# -*- coding: utf-8 -*-
from datetime import datetime
from parser.agent import TaiwanHotelParserAgent
from settings.config import Config
from store.excel import ExcelStore


def ask_city():
    print("寫選擇要抓取的資料: ")
    cities_code = Config.CITIES_CODE
    for city_code in cities_code.keys():
        print("縣市: {}, 輸入的代碼: {}".format(cities_code[city_code], city_code))
    city_code = input("請輸入代碼 (大寫) >> ").upper()
    if city_code not in cities_code.keys():
        print("不存在此代碼，請重新執行！")
        exit()
    return city_code


def main():
    city_code = ask_city()
    # 保存要抓取的縣市 xlsx 名稱
    begin = datetime.now()
    filename = Config.CITIES_CODE[city_code] + "所有旅宿統計資料.xlsx"
    excelstore = ExcelStore(filename)
    hotel_parser = TaiwanHotelParserAgent(city_code)
    hotel_parser.parsing(excelstore)
    end = datetime.now()
    print(f" ! Finish - beginning: {begin}, end: {end}, spent: {end - begin}")


if __name__ == "__main__":
    main()
