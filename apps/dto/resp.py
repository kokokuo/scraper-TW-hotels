# -*- coding: utf-8 -*-
from dataclasses import dataclass


@dataclass
class SyncHttpResponse(object):
    """
    已經同步後取區 aiohttp 返回的 ClientResponse 資料
    Args:
        raw_content (bytes): Bytes 格式的 HTML 內容
        text (str): Str 格式的 HTML 內容
        status_code (str): 狀態碼
        headers (dict): 回傳的 Headers
        cookies (dict): 回傳的 Cookies
        url (URL): 回傳的 URL
    """
    raw_content: bytes
    text: str
    status_code: int
    headers: dict
    cookies: dict
    url: str

