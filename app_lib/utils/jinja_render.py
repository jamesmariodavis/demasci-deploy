from typing import Dict, Any, Collection, Union
import pandas as pd
import plotly
import plotly.graph_objs as go
from jinja2 import (
    Environment,
    FileSystemLoader,
)
from app_lib.app_paths import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class JinjaRender:
    LIST_OF_FIGURES_TEMPLATE = 'list_of_items.html'

    @staticmethod
    def render_template(template_name: str, params: Dict[str, Any]) -> str:
        template_object = env.get_template(template_name)
        rendered_object = template_object.render(**params)
        return rendered_object

    @staticmethod
    def get_html_table_from_frame(frame: pd.DataFrame) -> str:
        html_str = frame.to_html()
        return html_str

    @staticmethod
    def get_html_div_from_figure(figure: go.Figure) -> str:
        html_div = plotly.io.to_html(fig=figure, include_plotlyjs='cdn', full_html=False)
        return html_div

    @staticmethod
    def render_list_of_items_to_html(list_of_items: Collection[Union[go.Figure, pd.DataFrame, str]]) -> str:
        html_divs = []
        for item in list_of_items:
            if isinstance(item, str):
                html_div = item
            elif isinstance(item, go.Figure):
                html_div = JinjaRender.get_html_div_from_figure(figure=item)
            elif isinstance(item, pd.DataFrame):
                html_div = JinjaRender.get_html_table_from_frame(frame=item)
            else:
                err_str = 'items of type {} not supported'.format(type(item))
                raise ValueError(err_str)
            html_divs.append(html_div)
        html_str = JinjaRender.render_template(
            template_name=JinjaRender.LIST_OF_FIGURES_TEMPLATE,
            params={'list_of_items': html_divs},
        )
        return html_str
