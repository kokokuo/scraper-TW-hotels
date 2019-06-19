# -*- coding: utf-8 -*-
import asyncio
from typing import List
from datetime import datetime
from apps.assembler.hotel import HotelContentRowsAssembler
from apps.dto.hotel import HotelContentRow
from apps.services.scraper import hotels_scraping_service
from apps.services.storer import HotelStoringExcelService, HotelStoringJsonService
from infra.logging import scraping_logger
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


async def parse_to_excel(city_name: str):
    filename = city_name + "所有旅宿統計資料.xlsx"
    stroing_excel_service = HotelStoringExcelService(filename, scraping_logger)
    counties = await hotels_scraping_service.find_counties(city_name)
    for county in counties:
        hotels = await hotels_scraping_service.find_hotels_by_county(city_name, county)
        hotel_rows: List[HotelContentRow] = HotelContentRowsAssembler().assemble(hotels)
        await stroing_excel_service.store(county.name,
                                          Config.PARSED_COLUMNS,
                                          hotel_rows,
                                          filename)
    stroing_excel_service.close()


async def parse_to_json(city_name: str):
    filename = city_name + "所有旅宿統計資料.json"
    storing_json_service = HotelStoringJsonService(scraping_logger)
    counties = await hotels_scraping_service.find_counties(city_name)
    for county in counties:
        hotels = await hotels_scraping_service.find_hotels_by_county(city_name, county)
        hotel_rows: List[HotelContentRow] = HotelContentRowsAssembler().assemble(hotels)
        await storing_json_service.store(county.name, hotel_rows, filename)


async def parsing(city_name: str, save_option: str):
    if save_option == Config.SAVE_EXCEL_TYPE:
        await parse_to_excel(city_name)
    else:
        await parse_to_json(city_name)


def main():
    city_code = ask_city()
    save_option = ask_save_option()
    city_name = Config.CITIES_CODE[city_code]
    # 保存要抓取的縣市 xlsx 名稱
    begin = datetime.now()
    parsing_corountine = parsing(city_name, save_option)
    asyncio.run(parsing_corountine)
    end = datetime.now()

    print(f"\n [ {colorful.bold_green}Finish{colorful.reset} ]    beginning: {begin}, end: {end}, spent: {end - begin} \n")


if __name__ == "__main__":
    main()
