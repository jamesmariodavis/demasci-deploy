from typing import List, Any
from googleapiclient.discovery import build
import pandas as pd

MAX_CELL_RANGE = 'A1:ZZ999999'


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

    def get_sheet_as_frame(
        self,
        spreadsheet_id: str,
        sheet_name: str,
        first_row_is_column_names: bool = False,
    ) -> Any:
        values = self.get_values_from_range(
            spreadsheet_id=spreadsheet_id,
            sheet_name=sheet_name,
            cell_range=MAX_CELL_RANGE,
        )
        frame = pd.DataFrame(values)
        if first_row_is_column_names:
            frame.columns = frame.iloc[0]
            frame = frame[1:].reset_index(drop=True)
        return frame
