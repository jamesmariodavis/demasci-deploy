from enum import Enum
from typing import Collection, Optional
import pandas as pd
import plotly
import plotly.graph_objs as go
from app_lib import JinjaRender


class ScatterMode(Enum):
    MARKERS = 'markers'
    LINE_AND_MARKERS = 'lines+markers'
    LINE = 'lines'


class PlotlyHelpers:
    SCATTER_MODE = ScatterMode

    @staticmethod
    def get_html_div_from_figure(figure: plotly.graph_objs.Figure) -> str:
        html_div = plotly.io.to_html(fig=figure, include_plotlyjs='cdn', full_html=False)
        return html_div

    @staticmethod
    def get_emtpy_figure() -> go.Figure:
        return go.Figure()

    @staticmethod
    def add_scatter_plot_to_figure(
        figure: go.Figure,
        frame: pd.DataFrame,
        x_column_name: str,
        y_column_name: str,
        scatter_mode: ScatterMode,
        plot_name: Optional[str] = None,
    ) -> None:
        # add default plot name
        if plot_name is None:
            plot_name = '{} vs {}'.format(y_column_name, x_column_name)
        scatter_trace = go.Scattergl(
            x=frame[x_column_name],
            y=frame[y_column_name],
            name=plot_name,
            mode=scatter_mode.value,
        )
        figure.add_trace(scatter_trace)

    @staticmethod
    def render_figures_to_html(figures: Collection[go.Figure]) -> str:
        html_divs = []
        for figure in figures:
            html_div = PlotlyHelpers.get_html_div_from_figure(figure=figure)
            html_divs.append(html_div)
        html_str = JinjaRender.render_template(
            template_name=JinjaRender.LIST_OF_FIGURES_TEMPLATE,
            params={'figures': html_divs},
        )
        return html_str
