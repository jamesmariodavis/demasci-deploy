from tests.base_test_case import BaseTestCase
from app_lib.data_access.google_sheets_service import GoogleSheetsService
import pytest

TEST_SHEET_ID = '1Uxi1SXc8CkpZcMPPmMrN5Z-8VRZXc1u62LFQVwkuMhs'
SHEET1 = 'Sheet1'
SHEET2 = 'Sheet2'


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


if __name__ == '__main__':
    pytest.main()