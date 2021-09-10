from typing import List, Any
from unittest.mock import patch
import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from app_lib.data_access.google_sheets_service import GoogleSheetsService

TEST_SHEET_ID = '1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs'
SHEET1 = 'Sheet1'
SHEET2 = 'Sheet2'

# test sheet: https://docs.google.com/spreadsheets/d/1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs


def patch_get_values_from_range(
    # pylint: disable=unused-argument
    self: GoogleSheetsService,
    spreadsheet_id: str,
    sheet_name: str,
    cell_range: str,
) -> List[List[Any]]:
    # cell data is the values without header
    values: List[List[Any]] = [['a', 'b'], ['1', '4'], [None, '0']]
    return values


class TestGoogleSheets(BaseTestCase):
    @pytest.mark.external_deps
    def test_get_values_from_range(self) -> None:
        google_sheets_service = GoogleSheetsService()
        returned_values = google_sheets_service.get_values_from_range(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            cell_range='A1:B3',
        )
        expected_values = [['a', 'b'], ['1'], ['2', '3']]
        self.assertListEqual(returned_values, expected_values)

    @pytest.mark.external_deps
    def test_get_sheet_as_frame(self) -> None:
        google_sheets_service = GoogleSheetsService()
        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=False,
        )
        expected_frame = pd.DataFrame({
            0: ['a', '1', '2', ''],
            1: ['b', None, '3', '7'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=True,
        )
        expected_frame = pd.DataFrame({
            'a': ['1', '2', ''],
            'b': [None, '3', '7'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

    @patch.object(
        target=GoogleSheetsService,
        attribute='get_values_from_range',
        new=patch_get_values_from_range,
    )
    def test_get_sheet_as_frame_local(self) -> None:
        google_sheets_service = GoogleSheetsService()
        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=False,
        )
        expected_frame = pd.DataFrame({
            0: ['a', '1', None],
            1: ['b', '4', '0'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)

        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            first_row_is_column_names=True,
        )
        expected_frame = pd.DataFrame({
            'a': ['1', None],
            'b': ['4', '0'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)


if __name__ == '__main__':
    pytest.main([__file__])
