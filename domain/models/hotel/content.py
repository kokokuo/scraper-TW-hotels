from typing import Optional


class HotelContent(object):
    def __init__(self,
                 id: int,
                 name: str,
                 phone: str,
                 addr: str,
                 rooms: str,
                 prices: str,
                 email: str,
                 url: str) -> None:

        self._id = id
        self._name = name
        self._address = addr
        self._phone = phone
        self._url = url
        self._email = email
        self._rooms = rooms
        self._prices = prices

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @property
    def phone(self) -> str:
        return self._phone

    @property
    def url(self) -> str:
        return self._url

    @property
    def email(self) -> str:
        return self._email

    @property
    def rooms(self) -> str:
        return self._rooms

    @property
    def prices(self) -> str:
        return self._prices

    def __repr__(self):
        return "<HotelContent: id=%r\n\
            name=%r\n\
            address=%r\n\
            phone=%r\n\
            url=%r\n\
            email=%r\n\
            rooms=%r\n\
            prices=%r>" % (
            self._id,
            self._name,
            self._address,
            self._phone,
            self._url,
            self._email,
            self._rooms,
            self._prices
        )


