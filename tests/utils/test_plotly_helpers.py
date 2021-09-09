import pytest
import pandas as pd
import plotly.graph_objs as go
from tests.base_test_case import BaseTestCase
from app_lib.utils.plotly_helpers import PlotlyHelpers


class TestGoogleSheets(BaseTestCase):
    def setUp(self) -> None:
        self.a_col = 'a'
        self.b_col = 'b'
        self.frame = pd.DataFrame({
            self.a_col: [1, 2],
            self.b_col: [3, 4],
        })
        return super().setUp()

    def test_get_empty_figure(self) -> None:
        returned_value = PlotlyHelpers.get_emtpy_figure()
        expected_value = go.Figure()
        self.assertEqual(returned_value, expected_value)
        self.assertEqual(0, len(returned_value.data))

    def test_add_scatter_plot_to_figure(self) -> None:
        figure = PlotlyHelpers.get_emtpy_figure()
        self.assertEqual(0, len(figure.data))

        # test add plot
        returned_value = PlotlyHelpers.add_scatter_plot_to_figure(
            figure=figure,
            frame=self.frame,
            x_column_name=self.a_col,
            y_column_name=self.b_col,
            plot_name='plotty',
            scatter_mode=PlotlyHelpers.SCATTER_MODE.LINE,
        )
        expected_value = None
        self.assertEqual(returned_value, expected_value)
        self.assertEqual(1, len(figure.data))


if __name__ == '__main__':
    pytest.main([__file__])
