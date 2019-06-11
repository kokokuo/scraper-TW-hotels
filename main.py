# -*- coding: utf-8 -*-
import xlsxwriter
from parser.agent import TaiwanHotelParserAgent
from parser.settings import TaiwanHotelConfig
from store.excel import ExcelStore


def main():
    print("寫選擇要抓取的資料: ")
    cities_code = TaiwanHotelConfig.CITIES_CODE
    for city_code in cities_code.keys():
        print("縣市: {}, 輸入的代碼: {}".format(cities_code[city_code], city_code))
    city_code = input("請輸入代碼 (大寫) >> ").upper()
    if city_code not in cities_code.keys():
        print("不存在此代碼，請重新執行！")
        exit()

    # 保存要抓取的縣市 xlsx 名稱
    filename = cities_code[city_code] + "所有旅宿統計資料.xlsx"
    excelstore = ExcelStore(filename)
    # workbook = xlsxwriter.Workbook(taiwan_cities_code[city_code] + "所有旅宿統計資料.xlsx")
    hotel_parser = TaiwanHotelParserAgent(city_code)
    hotel_parser.parsing(excelstore)


if __name__ == "__main__":
    main()
