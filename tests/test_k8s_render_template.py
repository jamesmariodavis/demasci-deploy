import pytest
from k8s.k8s_render_template import _replace_variables_with_args
from tests.base_test_case import BaseTestCase


class TestK8sRenderTemplate(BaseTestCase):
    def test_replace_variables_with_args(self) -> None:
        str_with_var = 'before {{VAR}} after'
        returned_result = _replace_variables_with_args(
            original_str=str_with_var,
            replacement_dict={'VAR': 'stuff'},
        )
        expected_result = 'before stuff after'
        self.assertEqual(returned_result, expected_result)


if __name__ == '__main__':
    pytest.main([__file__])
