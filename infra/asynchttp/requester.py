from urllib import parse
from typing import Optional
from lxml import etree
from aiohttp import ClientSession
from tenacity import retry
from tenacity import retry_if_exception_type, stop_after_attempt, wait_fixed
from infra.excepts.types import ReqSysAbnoramlError
from infra.asynchttp.resp import SyncHttpResponse
from settings.config import Config


class RetryableRequester(object):
    def __init__(self, logger, abnormal_url: str) -> None:
        self._logger = logger
        self._abnormal_url = abnormal_url

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), retry=retry_if_exception_type(ReqSysAbnoramlError))
    async def get(self,
                  url: str,
                  params: dict,
                  headers: Optional[dict] = None,
                  cookies: Optional[dict] = None) -> SyncHttpResponse:
        try:
            encoded_params = parse.urlencode(params)
            async with ClientSession() as session:
                async with session.get(url, params=encoded_params, headers=headers, cookies=cookies) as resp:
                    sync_resp = SyncHttpResponse(await resp.read(),
                                                 await resp.text(),
                                                 resp.status,
                                                 resp.headers,
                                                 resp.cookies,
                                                 resp.url.human_repr())
                    self._logger.debug(f"Response Cookies: {sync_resp.cookies}")
                    await self._check_does_normal_resp(sync_resp)
            return sync_resp
        except ReqSysAbnoramlError as rse:
            self._logger.error(f" ！ 網站異常 ！ #########################################")
            self._logger.error(f">> 請求網址: {url}, params: {params}, headers: {headers}, cookies: {cookies}")
            self._logger.error(f">> 回應網址：{rse.url}, 頁面狀態碼： {rse.http_code}\n" + rse.content)
            raise rse

    async def _check_does_normal_resp(self, resp: SyncHttpResponse) -> bool:
        if resp.url == self._abnormal_url:
            lxmltree = etree.HTML(resp.raw_content)
            content = etree.tostring(lxmltree, method='html', pretty_print=True).decode('utf-8')
            raise ReqSysAbnoramlError(resp.status_code, "解析旅館資料異常！皆為 None", resp.url, content)
        return True
