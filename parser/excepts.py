

class ReqSysAbnoramlError(Exception):
    """
    作為識別該頁面為
    """
    def __init__(self, http_code: int, message: str, req_url: str, req_content: str) -> None:
        self._http_code = http_code
        self._message = message
        self._url = req_url
        self._content = req_content

    @property
    def http_code(self) -> int:
        return self._http_code

    @property
    def message(self) -> str:
        return self._message

    @property
    def url(self) -> str:
        return self._url

    @property
    def content(self) -> str:
        return self._content
