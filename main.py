# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime
from apps.assembler.hotel import HotelFieldRowsAssembler
from apps.services.scraper import hotels_scraping_service
from apps.services.storer import hotel_storing_service
from settings.config import Config


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


async def parsing(city_name: str, filename: str):
    counties = await hotels_scraping_service.find_counties(city_name)
    for county in counties:
        hotels = await hotels_scraping_service.find_hotels_by_county(city_name, county)
        hotel_rows = HotelFieldRowsAssembler().assemble(hotels)
        await hotel_storing_service.store2excel(county.name,
                                                Config.PARSED_COLUMNS,
                                                hotel_rows,
                                                filename)


def main():
    city_code = ask_city()
    city_name = Config.CITIES_CODE[city_code]
    # 保存要抓取的縣市 xlsx 名稱
    begin = datetime.now()
    filename = city_name + "所有旅宿統計資料.xlsx"
    asyncio.run(parsing(city_name, filename))
    end = datetime.now()
    print(f"\n [ Finish ]      beginning: {begin}, end: {end}, spent: {end - begin} \n")


if __name__ == "__main__":
    main()
