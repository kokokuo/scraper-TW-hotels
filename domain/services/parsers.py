from typing import List
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from domain.models.county import CountyVO
from settings.config import Config


class CountiesParser(object):
    def __init__(self, url: str):
        self._url = url
        self.CITY_SELECTOR_XPATH = "//*[@id='sel_city']"
        self.COUNTIES_OPTION_XPATH = "//*[@id='sel_area']/option"

    def extract_counties(self, city_name: str) -> List[CountyVO]:
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
        selector: Select = Select(driver.find_element_by_xpath(self.CITY_SELECTOR_XPATH))
        selector.select_by_value(city_name)
        counties_options = driver.find_elements_by_xpath(self.COUNTIES_OPTION_XPATH)
        counties: List[CountyVO] = [
            CountyVO(option.text, option.get_attribute("value"))
            for option in counties_options if option.get_attribute("value")
        ]
        return counties
