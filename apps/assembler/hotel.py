from typing import List
from apps.dto.hotel import HotelContentRow
from domain.models.hotel.content import HotelContentVO
from domain.models.hotel.field import HotelField


class HotelContentRowsAssembler(object):
    def assemble(self, hotels: List[HotelContentVO]) -> List[HotelContentRow]:
        rows: List[HotelContentRow] = []
        hotel: HotelContentVO
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
