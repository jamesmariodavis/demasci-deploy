import pytest
import pandas as pd
from tests.base_test_case import BaseTestCase
from app_lib.utils.jinja_render import JinjaRender
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

    def test_render_template(self) -> None:
        template_name = JinjaRender.LIST_OF_FIGURES_TEMPLATE
        params = {'list_of_items': ['a', 'b']}
        returned_value = JinjaRender.render_template(
            template_name=template_name,
            params=params,
        )
        expected_value = '<!DOCTYPE html>\n<html lang="en">\n\n<head>\n    <meta charset="UTF-8">\n    <title>Report</title>\n</head>\n\n<body>\n    \n    a\n    \n    b\n    \n</body>\n\n</html>'
        self.assertEqual(returned_value, expected_value)

    def test_get_html_table_from_frame(self) -> None:
        frame = pd.DataFrame({
            'a': [1, 2],
            'b': [3, None],
        })
        returned_value = JinjaRender.get_html_table_from_frame(frame=frame)
        expected_value = '<table border="1" class="dataframe">\n  <thead>\n    <tr style="text-align: right;">\n      <th></th>\n      <th>a</th>\n      <th>b</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      <td>1</td>\n      <td>3.0</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>2</td>\n      <td>NaN</td>\n    </tr>\n  </tbody>\n</table>'
        self.assertEqual(returned_value, expected_value)

    def test_get_html_div_from_figure(self) -> None:
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

        # test render
        returned_value = JinjaRender.get_html_div_from_figure(figure=figure)
        # return object is too long to test exactly
        assert isinstance(returned_value, str)
        assert 'responsive' in returned_value

    def test_render_figures_and_frames_to_html(self) -> None:
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

        # test render
        returned_value = JinjaRender.render_list_of_items_to_html(list_of_items=[
            figure,
            self.frame,
            'hello!',
        ])
        returned_value_double = JinjaRender.render_list_of_items_to_html(list_of_items=[
            figure,
            self.frame,
            'hello!',
            figure,
        ])
        # return object is too long to test exactly
        assert isinstance(returned_value, str)
        assert 'responsive' in returned_value
        self.assertGreater(len(returned_value_double), len(returned_value))

        with self.assertRaises(ValueError):
            _ = JinjaRender.render_list_of_items_to_html(list_of_items=[1])


if __name__ == '__main__':
    pytest.main([__file__])
