import os
import re
import pytest
from tests.base_test_case import BaseTestCase
from app_lib.utils.file_parsing_helpers import FileParsingHelpers, ParsingException
from app_lib.app_paths import TEST_FIXTURE_DIR

TEST_K8S_YAML = os.path.join(TEST_FIXTURE_DIR, 'k8s.yml')
TEST_TEXT_FILE = os.path.join(TEST_FIXTURE_DIR, 'text_file.txt')


class TestFileParsingHelpers(BaseTestCase):
    def test_get_k8s_yaml_list(self) -> None:
        returned_result = FileParsingHelpers.get_k8s_yaml_list(file_path=TEST_K8S_YAML)
        expected_result = [{
            'apiVersion': 'apps/v1',
            'spec': {
                'selector': {
                    'matchLabels': {
                        'app': 'python-api'
                    }
                }
            }
        }, {
            'apiVersion': 'v1',
            'spec': {
                'ports': [{
                    'port': 5001,
                    'protocol': 'TCP',
                    'targetPort': 5001,
                }]
            }
        }]
        self.assertListEqual(returned_result, expected_result)

    def test_get_pattern_matches_from_file(self) -> None:
        # test unique capture
        returned_result = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=re.compile(r'^this is(.*)line'),
            file_path=TEST_TEXT_FILE,
            expect_unique_match=True,
        )
        expected_result = [' a ']
        self.assertEqual(returned_result, expected_result)

        # test empty capture
        returned_result = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=re.compile(r'^will not match(.*)line'),
            file_path=TEST_TEXT_FILE,
            expect_unique_match=False,
        )
        expected_result = []
        self.assertEqual(returned_result, expected_result)

        # test empty capture raises error
        with self.assertRaises(ParsingException):
            returned_result = FileParsingHelpers.get_pattern_matches_from_file(
                match_object=re.compile(r'^will not match(.*)line'),
                file_path=TEST_TEXT_FILE,
                expect_unique_match=True,
            )

        # test multi capture
        returned_result = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=re.compile(r'^here is some(.*)\n'),
            file_path=TEST_TEXT_FILE,
            expect_unique_match=False,
        )
        expected_result = [' text', ' more text']
        self.assertEqual(returned_result, expected_result)

        # test multi capture raises error
        with self.assertRaises(ParsingException):
            returned_result = FileParsingHelpers.get_pattern_matches_from_file(
                match_object=re.compile(r'^here is some(.*)\n'),
                file_path=TEST_TEXT_FILE,
                expect_unique_match=True,
            )

        # test multi capture groups raises error
        with self.assertRaises(ParsingException):
            returned_result = FileParsingHelpers.get_pattern_matches_from_file(
                match_object=re.compile(r'^here(.*)some(.*)\n'),
                file_path=TEST_TEXT_FILE,
                expect_unique_match=False,
            )


if __name__ == '__main__':
    pytest.main([__file__])
