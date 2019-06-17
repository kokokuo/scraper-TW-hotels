import random
from fake_useragent import UserAgent


class FakeHeaderGenerator(object):
    def __init__(self, logger) -> None:
        self._logger = logger

    async def generate(self) -> dict:
        """
        產生訪問網頁用的假 Header
        Returns:
            [dict]: 產生好的假 Header 標頭
        """
        fake_ua = UserAgent()
        random_ua = random.choice([fake_ua.chrome,
                                   fake_ua.opera,
                                   fake_ua.ie,
                                   fake_ua.firefox,
                                   fake_ua.safari,
                                   fake_ua.google,
                                   fake_ua.ff,
                                   fake_ua.random])
        header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Host": "taiwanstay.net.tw",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random_ua
        }
        self._logger.debug("產生的 Fake Header: {}".format(header["User-Agent"]))
        return header
