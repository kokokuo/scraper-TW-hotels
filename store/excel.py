import re
from typing import Optional, List
from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from parser.dto import HotelInfo, HotelField


class ExcelStore(object):
    def __init__(self, filename: str) -> None:
        self._workbook = Workbook(filename)

    def _format_cell(self) -> None:
        # 定義格式
        cell_format = self._workbook.add_format({"bold": True, "bg_color": "#D8F6CE", "font_size": 14})
        content_format = self._workbook.add_format({"font_size": 12})
        link_format = self._workbook.add_format({"color": "blue", "underline": 1, "font_size": 12})

    def _retrieve_header(self, parsed_column: HotelField):
        return parsed_column.value

    def add_sheet(self,
                  sheetname: str,
                  parsed_columns: List[HotelField],
                  column_width: int = 20) -> Worksheet:

        first_column = 0
        sheet = self._workbook.add_worksheet(sheetname)
        sheet.set_column(first_column, len(parsed_columns) - 1, column_width)

        header_columns = map(self._retrieve_header, parsed_columns)
        # 定義格式
        cell_format = self._workbook.add_format({"bold": True, "bg_color": "#D8F6CE", "font_size": 14})
        # 寫入第一列標題
        sheet.write_row(0, 0, header_columns, cell_format)
        return sheet

    def _normializa_url(self, source: str) -> str:
        """
        # 對 URL 做加工，如果 URL 沒有 https:// 或 http:// 則補上使其連結可以點擊
        Args:
            source (str): 來源網址
        Returns:
            str: 回傳網址，若無內容回傳空字串
        """
        pattern = r"^https?:\/{2}"
        if source:
            if re.search(pattern, source) is None:
                return "http://" + source
            return source
        return ""

    def store_hotel(self,
                    sheet: Worksheet,
                    row: int,
                    parsed_columns: List[HotelField],
                    hotel: HotelInfo) -> None:

        parsed_header: HotelField
        # 由 Columns 尋訪，並找出資料欄位
        for col, header in enumerate(parsed_columns):
            if header is HotelField.Url:
                url = hotel[header]
                url = self._normializa_url(url)
                link_style = {"color": "blue", "underline": 1, "font_size": 12}
                link_format = self._workbook.add_format(link_style)
                sheet.write_url(row, col, url, link_format)
            elif header is HotelField.Rooms:
                number_style = {"font_size": 12}
                number_format = self._workbook.add_format(number_style)
                sheet.write_number(row, col, int(hotel[header]), number_format)
            else:
                # 如果資料為 None 改成空字串
                field_data = hotel[header] if hotel[header] else ""
                sheet.write_string(row, col, field_data)

    def close(self):
        self._workbook.close()
