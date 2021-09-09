from enum import Enum
from typing import Optional
import pandas as pd
import plotly.graph_objs as go


class ScatterMode(Enum):
    MARKERS = 'markers'
    LINE_AND_MARKERS = 'lines+markers'
    LINE = 'lines'


class PlotlyHelpers:
    SCATTER_MODE = ScatterMode

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
