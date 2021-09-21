from typing import (
    List,
    Dict,
    Union,
    Any,
)
import re
import yaml


class ParsingException(Exception):
    pass


class FileParsingHelpers:
    @staticmethod
    def get_k8s_yaml_list(file_path: str) -> List[Union[List[Any], Dict[str, Any]]]:
        with open(file_path, 'r', encoding='utf8') as f:
            k8s_yml_str = f.read()
        # k8s yaml files may have multiple sub yamls
        # some sub yamls may be empty
        sub_yml_strs = k8s_yml_str.split('---')
        sub_ymls = [yaml.safe_load(i) for i in sub_yml_strs if i]
        return sub_ymls

    @staticmethod
    def get_pattern_matches_from_file(
        match_object: re.Pattern,  # type: ignore
        file_path: str,
        expect_unique_match: bool = True,
    ) -> List[str]:
        with open(file_path, 'rt', encoding='utf-8') as f:
            lines = f.readlines()
        target_lines = [match_object.match(i) for i in lines]
        non_null_target_lines = [i for i in target_lines if i is not None]
        if not non_null_target_lines and expect_unique_match:
            err_str = 'found no matchs for {} in {}'.format(
                match_object,
                file_path,
            )
            raise ParsingException(err_str)
        try:
            target_strings = [i.group(1) for i in non_null_target_lines]
        except IndexError as e:
            err_str = 'extracting group(1) failed on {} using regex {}'.format(
                non_null_target_lines,
                match_object,
            )
            raise ParsingException(err_str) from e
        if (len(target_strings) != 1) and expect_unique_match:
            err_str = 'did not find unique match for {} in {}'.format(
                match_object.pattern,
                file_path,
            )
            raise ParsingException(err_str)
        # verify that there are not multiple capture groups when capture found
        if len(target_strings) > 0:
            num_capture_groups = len(non_null_target_lines[0].groups())
            if num_capture_groups > 1:
                err_str = 'found more that 1 capture group in regex {}'.format(match_object)
                raise ParsingException(err_str)
        return target_strings
