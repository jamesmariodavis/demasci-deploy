import unittest
import pandas as pd


class BaseTestCase(unittest.TestCase):
    @staticmethod
    def assertFramesEqual(
        frame1: pd.DataFrame,
        frame2: pd.DataFrame,
    ) -> None:
        # test whether two frames are equal, regardless of column or row ordering
        # copy frames to avoid mutating originals
        frame1_copy = frame1.copy()
        frame2_copy = frame2.copy()

        BaseTestCase.assertFrameColumnsEqual(
            frame1=frame1_copy,
            frame2=frame2_copy,
        )

        frame1_cols = sorted(list(frame1.columns))
        frame2_cols = sorted(list(frame2.columns))

        # reorder columns
        frame1_copy = frame1_copy[frame1_cols]
        frame2_copy = frame2_copy[frame2_cols]

        # sort rows
        frame1_copy = frame1_copy.sort_values(frame1_cols).reset_index(drop=True)
        frame2_copy = frame2_copy.sort_values(frame2_cols).reset_index(drop=True)

        if not frame1_copy.equals(frame2_copy):
            err_str = '\nframe1\n{}\n\nframe2\n{}\n'.format(
                frame1,
                frame2,
            )
            raise AssertionError(err_str)

    @staticmethod
    def assertSeriesEqual(
        series1: pd.Series,
        series2: pd.Series,
    ) -> None:
        series_are_equal = series1.equals(series2)
        if not series_are_equal:
            err_str = '\nseries1:{}\nseries2:{}\n'.format(
                series1,
                series2,
            )
            raise AssertionError(err_str)

    @staticmethod
    def assertFrameColumnsEqual(
        frame1: pd.DataFrame,
        frame2: pd.DataFrame,
    ) -> None:
        # test whether frame columns are equal regardless of ordering
        frame1_cols = sorted(list(frame1.columns))
        frame2_cols = sorted(list(frame2.columns))
        if frame1_cols != frame2_cols:
            err_str = '\nframe1_cols:{}\nframe2_cols:{}\n'.format(
                frame1_cols,
                frame2_cols,
            )
            raise AssertionError(err_str)
