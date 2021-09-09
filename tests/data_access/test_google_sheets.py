import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from app_lib.data_access.google_sheets_service import GoogleSheetsService

TEST_SHEET_ID = '1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs'
SHEET1 = 'Sheet1'
SHEET2 = 'Sheet2'

# test sheet: https://docs.google.com/spreadsheets/d/1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs


class TestGoogleSheets(BaseTestCase):
    @pytest.mark.external_deps
    def test_get_values_from_range(self) -> None:
        google_sheets_service = GoogleSheetsService()
        returned_values = google_sheets_service.get_values_from_range(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET1,
            cell_range='A1:B2',
        )
        expected_values = [['1'], ['2', '3']]
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
            0: ['1', '2'],
            1: [None, '3'],
        })
        # expected_frame[0] = expected_frame[0].astype(object)
        self.assertFramesEqual(returned_frame, expected_frame)

        returned_frame = google_sheets_service.get_sheet_as_frame(
            spreadsheet_id=TEST_SHEET_ID,
            sheet_name=SHEET2,
            first_row_is_column_names=True,
        )
        expected_frame = pd.DataFrame({
            'a': ['1', '2'],
            'b': ['3', '4'],
        })
        self.assertFramesEqual(returned_frame, expected_frame)


if __name__ == '__main__':
    pytest.main([__file__])
