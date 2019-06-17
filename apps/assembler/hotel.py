from typing import List
from apps.dto.hotel import HotelFieldRow
from domain.models.hotel.content import HotelContent
from domain.models.hotel.field import HotelField


class HotelFieldRowsAssembler(object):
    def assemble(self, hotels: List[HotelContent]) -> List[HotelFieldRow]:
        rows: List[HotelFieldRow] = []
        hotel: HotelContent
        for hotel in hotels:
            rows.append({
                HotelField.Id: str(hotel.id),
                HotelField.Name: hotel.name,
                HotelField.Phone: hotel.phone,
                HotelField.Address: hotel.address,
                HotelField.Rooms: hotel.rooms,
                HotelField.Prices: hotel.prices,
                HotelField.Email: hotel.email,
                HotelField.Url: hotel.url
            })
        return rows
