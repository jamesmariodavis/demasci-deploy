from typing import Dict, Any
from jinja2 import Environment, FileSystemLoader
from app_lib.app_paths import TEMPLATE_DIR

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))


class JinjaRender:
    LIST_OF_FIGURES_TEMPLATE = 'list_of_figures.html'

    @staticmethod
    def render_template(template_name: str, params: Dict[str, Any]) -> str:
        template_object = env.get_template(template_name)
        rendered_object = template_object.render(**params)
        return rendered_object
