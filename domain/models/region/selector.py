from typing import List
from logging import Logger
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from domain.models.region.county import CountyVO
from infra.logging import scraping_logger
from settings.config import Config


class SeleniumCountiesSelecor(object):
    def __init__(self,
                 url: str,
                 city_xpath: str,
                 counties_xpath: str,
                 scraping_logger: Logger):
        self._url = url
        self._city_xpath = city_xpath
        self._counties_xpath = counties_xpath
        self._logger = scraping_logger

    async def extract(self, city_name: str) -> List[CountyVO]:
        """
        藉由 Selenium 模擬點擊縣市，取得指定縣市的所有省區資料
        Returns:
            List[CountyVO]: 此城市的所有省區
        """

        options = webdriver.ChromeOptions()
        # 不開啟 Browser 的 GUI
        options.headless = True
        driver = webdriver.Chrome(chrome_options=options)
        driver.get(self._url)
        selector: Select = Select(driver.find_element_by_xpath(self._city_xpath))
        selector.select_by_value(city_name)
        counties_options = driver.find_elements_by_xpath(self._counties_xpath)
        counties: List[CountyVO] = [
            CountyVO(option.text, option.get_attribute("value"))
            for option in counties_options if option.get_attribute("value")
        ]
        self._logger.info(f" [ Extracted ]    完成網頁模擬點擊，取得「{city_name}」所有的市區鄉鎮")
        return counties


counties_selector = SeleniumCountiesSelecor(Config.WEBSITE_URL,
                                            Config.CITY_SELECTOR_XPATH,
                                            Config.COUNTIES_OPTION_XPATH,
                                            scraping_logger)
