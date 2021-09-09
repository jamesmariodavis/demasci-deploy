from typing import List
import pandas as pd
import plotly.graph_objs as go
from app_lib import (
    PlotlyHelpers,
    JinjaRender,
)

A_COL = 'a'
B_COL = 'b'
EXAMPLE_FRAME_1 = pd.DataFrame({
    A_COL: [1, 2, 5],
    B_COL: [3, 6, 1],
})
EXAMPLE_FRAME_2 = pd.DataFrame({
    A_COL: [1, 5, 7],
    B_COL: [1, 2, 1],
})
EXAMPLE_FRAME_3 = pd.DataFrame({
    A_COL: [-1, 2, 8],
    B_COL: [1, 2, -3],
})


def get_example_items() -> List[go.Figure]:
    # build figure 1
    figure_1 = PlotlyHelpers.get_emtpy_figure()
    PlotlyHelpers.add_scatter_plot_to_figure(
        figure=figure_1,
        frame=EXAMPLE_FRAME_1,
        x_column_name=A_COL,
        y_column_name=B_COL,
        scatter_mode=PlotlyHelpers.SCATTER_MODE.LINE,
    )
    PlotlyHelpers.add_scatter_plot_to_figure(
        figure=figure_1,
        frame=EXAMPLE_FRAME_2,
        x_column_name=A_COL,
        y_column_name=B_COL,
        scatter_mode=PlotlyHelpers.SCATTER_MODE.LINE,
    )

    # build figure 2
    figure_2 = PlotlyHelpers.get_emtpy_figure()
    PlotlyHelpers.add_scatter_plot_to_figure(
        figure=figure_2,
        frame=EXAMPLE_FRAME_3,
        x_column_name=A_COL,
        y_column_name=B_COL,
        scatter_mode=PlotlyHelpers.SCATTER_MODE.LINE,
    )

    list_of_items = [figure_1, figure_2, EXAMPLE_FRAME_1, EXAMPLE_FRAME_2]
    return list_of_items


def get_example_html_str() -> str:
    list_of_items = get_example_items()
    html_str = JinjaRender.render_list_of_items_to_html(list_of_items=list_of_items)
    return html_str
