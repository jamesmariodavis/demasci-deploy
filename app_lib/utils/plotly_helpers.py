from enum import Enum
import pandas as pd
import plotly
import plotly.graph_objs as go


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
        plot_name: str,
        scatter_mode: ScatterMode,
    ) -> None:
        scatter_trace = go.Scattergl(
            x=frame[x_column_name],
            y=frame[y_column_name],
            name=plot_name,
            mode=scatter_mode.value,
        )
        figure.add_trace(scatter_trace)
