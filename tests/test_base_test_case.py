import pandas as pd
import pytest
from tests.base_test_case import BaseTestCase


class TestBaseTestCase(BaseTestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame({
            'a': [1, 2],
            'b': [2, 3],
        })
        self.frame_same = pd.DataFrame({
            'a': [1, 2],
            'b': [2, 3],
        })
        self.frame_same_reorder = pd.DataFrame({
            'a': [2, 1],
            'b': [3, 2],
        })
        self.frame_cols_differ = pd.DataFrame({
            'a': [1, 2],
            'c': [2, 3],
        })
        self.frame_values_differ = pd.DataFrame({
            'a': [1, 2],
            'b': [2, 4],
        })
        return super().setUp()

    def test_assertFrameColumnsEqual(self) -> None:
        self.assertFrameColumnsEqual(self.frame, self.frame_same)
        self.assertFrameColumnsEqual(self.frame, self.frame_values_differ)
        with self.assertRaises(AssertionError):
            self.assertFrameColumnsEqual(self.frame, self.frame_cols_differ)

    def test_assertFramesEqual(self) -> None:
        self.assertFramesEqual(self.frame, self.frame_same)
        self.assertFramesEqual(self.frame, self.frame_same_reorder)
        with self.assertRaises(AssertionError):
            self.assertFramesEqual(self.frame, self.frame_cols_differ)
        with self.assertRaises(AssertionError):
            self.assertFramesEqual(self.frame, self.frame_values_differ)

    def test_assertSeriesEqual(self) -> None:
        series = pd.Series([1, 2])
        series_same = pd.Series([1, 2])
        series_diff = pd.Series([1, 3])
        self.assertSeriesEqual(series, series_same)
        with self.assertRaises(AssertionError):
            self.assertSeriesEqual(series, series_diff)


if __name__ == '__main__':
    pytest.main([__file__])
