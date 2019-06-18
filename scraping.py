# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
from apps.assembler.hotel import HotelFieldRowsAssembler
from apps.services.scraper import hotels_scraping_service
from apps.services.storer import hotel_storing_service
from settings.config import Config
import colorful


def ask_city():
    print("1. 請選擇要抓取的縣市 : ")
    cities_code = Config.CITIES_CODE
    for city_code in cities_code.keys():
        print("縣市: {}, 輸入的代碼: {}".format(cities_code[city_code], city_code))
    city_code = input("請輸入代碼 (大寫) >> ").upper()
    if city_code not in cities_code.keys():
        print("不存在此代碼，請重新執行！")
        exit()
    return city_code


def ask_save_option():
    print("2. 請選擇抓取下來後倒保存到形式：")
    save_option = input("儲存到 Excel (輸入 E)，或儲存到 Json (輸入 J)  >> ").upper()
    if save_option not in Config.SAVE_OPTIONS:
        print("不存在此代碼，只能選擇輸入 E 或是 J ")
        exit()
    return save_option


async def parsing(city_name: str, filename: str, save_option: str):
    counties = await hotels_scraping_service.find_counties(city_name)
    for county in counties:
        hotels = await hotels_scraping_service.find_hotels_by_county(city_name, county)
        hotel_rows = HotelFieldRowsAssembler().assemble(hotels)
        if save_option is Config.SAVE_EXCEL_TYPE:
            await hotel_storing_service.store2excel(county.name,
                                                    Config.PARSED_COLUMNS,
                                                    hotel_rows,
                                                    filename)
        else:
            print("尚未實作儲存 Json 格式的代碼 ！")


def main():
    city_code = ask_city()
    save_option = ask_save_option()
    city_name = Config.CITIES_CODE[city_code]
    # 保存要抓取的縣市 xlsx 名稱
    begin = datetime.now()
    filename = city_name + "所有旅宿統計資料.xlsx"
    parsing_corountine = parsing(city_name, filename, save_option)
    asyncio.run(parsing_corountine)
    end = datetime.now()

    print(f"\n [ {colorful.bold_green}Finish{colorful.reset} ]    beginning: {begin}, end: {end}, spent: {end - begin} \n")


if __name__ == "__main__":
    main()
