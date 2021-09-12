from typing import (
    List,
    Any,
    Dict,
)
from enum import Enum
from googleapiclient.discovery import build
import numpy as np
import pandas as pd


class ValueInputOption(Enum):
    RAW = 'RAW'
    USER_ENTERED = 'USER_ENTERED'


class MajorDimension(Enum):
    ROWS = 'ROWS'  # default
    COLUMNS = 'COLUMNS'


class CellData(Enum):
    # https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets/cells#CellData
    USER_ENTERED_VALUE = 'userEnteredValue'
    USER_ENTERED_FORMAT = 'userEnteredFormat'


def _get_sheet_service() -> Any:
    # pylint: disable=no-member
    service = build('sheets', 'v4')
    sheet = service.spreadsheets()  # type: ignore
    return sheet


def _get_sheet_name_and_range(
    sheet_name: str,
    cell_range: str,
) -> str:
    if cell_range:
        sheet_name_and_range = '{}!{}'.format(sheet_name, cell_range)
    else:
        sheet_name_and_range = sheet_name
    return sheet_name_and_range


class GoogleSheetsValuesUpdater:
    def __init__(self, spreadsheet_id: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.data: List[Dict[str, Any]] = []
        self.sheet = _get_sheet_service()

    def execute(self) -> None:
        body = {
            'valueInputOption': ValueInputOption.RAW.value,
            'data': self.data,
        }
        _ = self.sheet.values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body,
        ).execute()

    def add_data(
        self,
        sheet_name: str,
        cell_range: str,
        values: List[List[Any]],
    ) -> None:
        sheet_name_and_cell_range = _get_sheet_name_and_range(
            sheet_name=sheet_name,
            cell_range=cell_range,
        )
        update_range = {
            'values': values,
            'range': sheet_name_and_cell_range,
            'majorDimension': MajorDimension.ROWS.value,
        }
        self.data.append(update_range)


class GoogleSheetsValuesClear:
    def __init__(self, spreadsheet_id: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.range_names: List[str] = []
        self.sheet = _get_sheet_service()

    def execute(self) -> None:
        body = {'ranges': self.range_names}
        _ = self.sheet.values().batchClear(
            spreadsheetId=self.spreadsheet_id,
            body=body,
        ).execute()

    def add_clear_cell_data(
        self,
        sheet_name: str,
        cell_range: str,
    ) -> None:
        sheet_name_and_range = _get_sheet_name_and_range(
            sheet_name=sheet_name,
            cell_range=cell_range,
        )
        self.range_names.append(sheet_name_and_range)


class GoogleSheetsValuesGetter:
    def __init__(self, spreadsheet_id: str) -> None:
        self.spreadsheet_id = spreadsheet_id
        self.range_names: List[str] = []
        self.sheet = _get_sheet_service()

    def execute(self) -> List[List[Any]]:
        result = self.sheet.values().batchGet(
            spreadsheetId=self.spreadsheet_id,
            ranges=self.range_names,
            majorDimension=MajorDimension.ROWS.value,
        ).execute()
        ranges = result.get('valueRanges', [])
        values = [i.get('values', []) for i in ranges]
        return values

    def add_range(
        self,
        sheet_name: str,
        cell_range: str,
    ) -> None:
        sheet_name_and_range = _get_sheet_name_and_range(
            sheet_name=sheet_name,
            cell_range=cell_range,
        )
        self.range_names.append(sheet_name_and_range)


class GoogleSheetsService:
    @staticmethod
    def get_sheets_values_clear(spreadsheet_id: str) -> GoogleSheetsValuesClear:
        return GoogleSheetsValuesClear(spreadsheet_id=spreadsheet_id)

    @staticmethod
    def get_sheets_values_updater(spreadsheet_id: str) -> GoogleSheetsValuesUpdater:
        return GoogleSheetsValuesUpdater(spreadsheet_id=spreadsheet_id)

    @staticmethod
    def get_sheets_values_getter(spreadsheet_id: str) -> GoogleSheetsValuesGetter:
        return GoogleSheetsValuesGetter(spreadsheet_id=spreadsheet_id)

    @staticmethod
    def get_sheet_as_frame(
        spreadsheet_id: str,
        sheet_name: str,
        first_row_is_column_names: bool = False,
    ) -> Any:
        sheets_values_getter = GoogleSheetsValuesGetter(spreadsheet_id=spreadsheet_id)
        sheets_values_getter.add_range(
            sheet_name=sheet_name,
            cell_range='',
        )
        result = sheets_values_getter.execute()
        values = result[0]
        frame = pd.DataFrame(values)
        frame = frame.replace('', np.nan).fillna(np.nan)
        if first_row_is_column_names:
            frame.columns = frame.iloc[0]
            frame = frame[1:].reset_index(drop=True)
        return frame

    @staticmethod
    def write_frame_to_sheet(
        frame: pd.DataFrame,
        spreadsheet_id: str,
        sheet_name: str,
        write_columns_names: bool = True,
    ) -> Any:
        sheets_values_updater = GoogleSheetsValuesUpdater(spreadsheet_id=spreadsheet_id)
        list_of_rows = frame.values.tolist()
        if write_columns_names:
            list_of_rows.insert(0, list(frame.columns))
        sheets_values_updater.add_data(
            values=list_of_rows,
            sheet_name=sheet_name,
            cell_range='',
        )
        sheets_values_updater.execute()
