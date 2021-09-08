import pytest
from tests.base_test_case import BaseTestCase
from app_lib.utils.jinja_render import JinjaRender


class TestGoogleSheets(BaseTestCase):
    def test_render_template(self) -> None:
        template_name = JinjaRender.LIST_OF_FIGURES_TEMPLATE
        params = {'figures': ['a', 'b']}
        returned_value = JinjaRender.render_template(
            template_name=template_name,
            params=params,
        )
        expected_value = '<!DOCTYPE html>\n<html lang="en">\n\n<head>\n    <meta charset="UTF-8">\n    <title>Report</title>\n</head>\n\n<body>\n    \n    a\n    \n    b\n    \n</body>\n\n</html>'
        self.assertEqual(returned_value, expected_value)


if __name__ == '__main__':
    pytest.main([__file__])
