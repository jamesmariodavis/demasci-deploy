from googleapiclient.discovery import build
from typing import List, Any


class GoogleSheetsService:
    def __init__(self) -> None:
        # pylint: disable=no-member
        service = build('sheets', 'v4')
        self.sheet = service.spreadsheets()  # type: ignore

    def get_values_from_range(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        cell_range: str,
    ) -> List[List[Any]]:
        sheet_name_and_range = '{}!{}'.format(sheet_name, cell_range)
        result = self.sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=sheet_name_and_range,
        ).execute()
        values = result.get('values', [])
        return values
