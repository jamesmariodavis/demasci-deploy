from typing import List, Any
from unittest.mock import patch
import pytest
import pandas as pd
import numpy as np
from tests.base_test_case import BaseTestCase
from app_lib.data_access.google_sheets_service import (
    GoogleSheetsService,
    GoogleSheetsValuesGetter,
)

# test sheet: https://docs.google.com/spreadsheets/d/1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs
TEST_SHEET_ID = '1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs'
SHEET1 = 'Sheet1'
SHEET2 = 'Sheet2'


def patch_values_getter_execute(
    # pylint: disable=unused-argument
    self: GoogleSheetsValuesGetter, ) -> List[List[Any]]:
    # cell data is the values without header
    values: List[List[Any]] = [
        [['a', 'b'], ['4'], ['', '0']],
    ]
    return values


class TestGoogleSheets(BaseTestCase):
    @pytest.mark.external_deps
    def test_google_sheets_value_getter(self) -> None:
        value_getter = GoogleSheetsService.get_sheets_values_getter(spreadsheet_id=TEST_SHEET_ID)
        value_getter.add_range(
            sheet_name=SHEET1,
            cell_range='',
        )
        value_getter.add_range(
            sheet_name=SHEET1,
            cell_range='A1:B2',
        )
        returned_value = value_getter.execute()
        expected_value = [
            [
                ['a', 'b'],
                ['1'],
                ['2', '3'],
                ['', '7'],
            ],
            [
                ['a', 'b'],
                ['1'],
            ],
        ]
        self.assertListEqual(returned_value, expected_value)

    @pytest.mark.external_deps
    def test_google_sheets_update_cycle(self) -> None:
        value_to_write = [['1', '2'], ['a', '7']]
        # write data to sheet
        value_updater = GoogleSheetsService.get_sheets_values_updater(spreadsheet_id=TEST_SHEET_ID)
        value_updater.add_data(
            sheet_name=SHEET2,
            cell_range='',
            values=value_to_write,
        )
        value_updater.execute()

        # verify data has been written
        value_getter = GoogleSheetsService.get_sheets_values_getter(spreadsheet_id=TEST_SHEET_ID)
        value_getter.add_range(
            sheet_name=SHEET2,
            cell_range='',
        )
        returned_value = value_getter.execute()
        expected_value = [value_to_write]
        self.assertListEqual(returned_value, expected_value)

        # clear data
        value_clear = GoogleSheetsService.get_sheets_values_clear(spreadsheet_id=TEST_SHEET_ID)
        value_clear.add_clear_cell_data(
            sheet_name=SHEET2,
            cell_range='',
        )
        value_clear.execute()

        # verify data has been cleared
        value_getter = GoogleSheetsService.get_sheets_values_getter(spreadsheet_id=TEST_SHEET_ID)
        value_getter.add_range(
            sheet_name=SHEET2,
            cell_range='',
        )
        returned_value = value_getter.execute()
        expected_value = [[]]
        self.assertListEqual(returned_value, expected_value)

    @pytest.mark.external_deps
    def test_get_sheet_as_frame(self) -> None:
        google_sheets_service = GoogleSheetsService()
        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=False,
        )
        expected_frame = pd.DataFrame({
            0: ['a', '1', '2', np.nan],
            1: ['b', np.nan, '3', '7'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=True,
        )
        expected_frame = pd.DataFrame({
            'a': ['1', '2', np.nan],
            'b': [np.nan, '3', '7'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

    @patch.object(
        target=GoogleSheetsValuesGetter,
        attribute='execute',
        new=patch_values_getter_execute,
    )
    def test_get_sheet_as_frame_local(self) -> None:
        returned_frame = GoogleSheetsService.get_sheet_as_frame(
            spreadsheet_id='junk',
            sheet_name='junk',
            first_row_is_column_names=False,
        )
        expected_frame = pd.DataFrame({
            0: ['a', '4', np.nan],
            1: ['b', np.nan, '0'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

        returned_frame = GoogleSheetsService.get_sheet_as_frame(
            spreadsheet_id='junk',
            sheet_name='junk',
            first_row_is_column_names=True,
        )
        expected_frame = pd.DataFrame({
            'a': ['4', np.nan],
            'b': [np.nan, '0'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

    @pytest.mark.external_deps
    def test_write_frame_to_sheet(self) -> None:
        frame_to_write = pd.DataFrame({
            'a': ['1', '2'],
            'b': ['3', '4'],
        })
        GoogleSheetsService.write_frame_to_sheet(
            frame=frame_to_write,
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET2,
            write_columns_names=True,
        )
        returned_frame = GoogleSheetsService.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET2,
            first_row_is_column_names=True,
        )
        self.assertFramesEqual(frame_to_write, returned_frame)

        # clear data
        value_clear = GoogleSheetsService.get_sheets_values_clear(spreadsheet_id=TEST_SHEET_ID)
        value_clear.add_clear_cell_data(
            sheet_name=SHEET2,
            cell_range='',
        )
        value_clear.execute()


if __name__ == '__main__':
    pytest.main([__file__])
