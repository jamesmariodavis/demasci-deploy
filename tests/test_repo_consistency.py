# tests that repo conforms to expectations
from typing import List
import os
import re
import subprocess
import json5
from app_lib.app_paths import ROOT_DIR


class ConsistencyException(Exception):
    pass


RESERVED_PORTS = (
    8001,  # k8s dashboard
    5001,  # k8s uvicorn port defined in k8s/uvicorn.yml
)

CONFIGURE_FILE_PATH = os.path.join(ROOT_DIR, 'configure.sh')
GITIGNORE_FILE_PATH = os.path.join(ROOT_DIR, '.gitignore')
DEVCONTAINER_JSON_FILE_PATH = os.path.join(ROOT_DIR, '.devcontainer', 'devcontainer.json')
POETRY_TOML_FILE_PATH = os.path.join(ROOT_DIR, 'pyproject.toml')
DOCKERFILE_FILE_PATH = os.path.join(ROOT_DIR, 'docker', 'Dockerfile')


def assert_all_files_windows_compatible() -> None:
    std_out_str = subprocess.check_output("git ls-files", shell=True)
    all_files = std_out_str.decode('utf8').split('\n')
    windows_incompatible_files = [file for file in all_files if re.compile(r'.*[:<>"\|\?\*\\].*').match(file)]
    if windows_incompatible_files:
        err_str = 'found files incompatible with windows naming scheme: {}'.format(windows_incompatible_files)
        raise ConsistencyException(err_str)


def _get_string_from_file(
        match_object: re.Pattern,  # type: ignore
        file_path: str,
        expect_unique_match: bool = True) -> List[str]:
    with open(file_path, 'rt', encoding='utf-8') as f:
        lines = f.readlines()
    target_lines = [match_object.match(i) for i in lines]
    non_null_target_lines = [i for i in target_lines if i is not None]
    if not non_null_target_lines:
        err_str = 'found no matchs for {} in {}'.format(
            match_object,
            file_path,
        )
        raise ConsistencyException(err_str)
    try:
        target_strings = [i.group(1) for i in non_null_target_lines]
    except IndexError as e:
        err_str = 'extracting group(1) failed on {} using regex {}'.format(
            non_null_target_lines,
            match_object,
        )
        raise ConsistencyException(err_str) from e
    if (len(target_strings) != 1) and expect_unique_match:
        err_str = 'did not find unique match for {} in {}'.format(
            match_object.pattern,
            file_path,
        )
        raise ConsistencyException(err_str)
    return target_strings


def assert_flask_app_names_correct() -> None:
    # retreive referenced module for api server
    flask_app_file_location_re = re.compile(r'^API_MODULE_LOCATION[]*=[]*(.*)')
    try:
        referenced_module_location = _get_string_from_file(
            match_object=flask_app_file_location_re,
            file_path=CONFIGURE_FILE_PATH,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            CONFIGURE_FILE_PATH,
            flask_app_file_location_re.pattern,
        )
        raise ConsistencyException(err_str) from e
    infered_python_file = '{}.py'.format(referenced_module_location)
    infered_python_file_path = os.path.join(ROOT_DIR, infered_python_file)

    # check if referenced module exists
    if not os.path.exists(infered_python_file_path):
        err_str = '{} references flask module {}. does not exist'.format(
            CONFIGURE_FILE_PATH,
            infered_python_file,
        )
        raise ConsistencyException(err_str)

    # retreive referenced api app name
    docker_flask_app_name_re = re.compile(r'^API_APP_NAME_IN_CODE[ ]*=[ ]*(.*)')
    try:
        referenced_flask_app_name = _get_string_from_file(
            match_object=docker_flask_app_name_re,
            file_path=CONFIGURE_FILE_PATH,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            CONFIGURE_FILE_PATH,
            docker_flask_app_name_re.pattern,
        )
        raise ConsistencyException(err_str) from e

    # retreive actual api app name
    python_flask_app_name_re = re.compile(r'(.*) = FastAPI\(\).*')
    try:
        actual_flask_app_name = _get_string_from_file(
            match_object=python_flask_app_name_re,
            file_path=infered_python_file_path,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            infered_python_file_path,
            python_flask_app_name_re.pattern,
        )
        raise ConsistencyException(err_str) from e

    # verify same name
    if referenced_flask_app_name != actual_flask_app_name:
        err_str = 'flask app names inconsistent. Dockerfile reference: {}. Flask app name: {}.'.format(
            referenced_flask_app_name,
            actual_flask_app_name,
        )
        raise ConsistencyException(err_str)


def assert_port_values_consistent() -> None:
    with open(DEVCONTAINER_JSON_FILE_PATH, 'r', encoding='utf8') as f:
        devcontainer_json = json5.load(f)
    forward_ports = devcontainer_json['forwardPorts']
    vscode_injected_port_env_var = int(devcontainer_json['containerEnv']['PORT'])

    ray_dashboard_port_match_object = re.compile(r'^RAY_DASHBOARD_PORT[ ]*=[ ]*(.*)')
    api_test_port_match_object = re.compile(r'^API_TEST_PORT[ ]*=[ ]*(.*)')

    ray_dashboard_port = _get_string_from_file(
        match_object=ray_dashboard_port_match_object,
        file_path=CONFIGURE_FILE_PATH,
        expect_unique_match=True,
    )[0]
    api_test_port = _get_string_from_file(
        match_object=api_test_port_match_object,
        file_path=CONFIGURE_FILE_PATH,
        expect_unique_match=True,
    )[0]
    if not ray_dashboard_port:
        err_str = 'could not find ray dashboard port in {}'.format(CONFIGURE_FILE_PATH)
        raise ConsistencyException(err_str)

    if not api_test_port:
        err_str = 'could not find api test port in {}'.format(CONFIGURE_FILE_PATH)
        raise ConsistencyException(err_str)

    if int(ray_dashboard_port) not in forward_ports:
        err_str = 'ray dashboard port in {} not present in forward ports in {}'.format(
            CONFIGURE_FILE_PATH,
            DEVCONTAINER_JSON_FILE_PATH,
        )
        raise ConsistencyException(err_str)

    if int(api_test_port) not in forward_ports:
        err_str = 'api test port in {} not present in forward ports in {}'.format(
            CONFIGURE_FILE_PATH,
            DEVCONTAINER_JSON_FILE_PATH,
        )
        raise ConsistencyException(err_str)

    if int(api_test_port) != vscode_injected_port_env_var:
        err_str = 'api test port = {}. vscode injected port name = {}. must match'.format(
            api_test_port,
            vscode_injected_port_env_var,
        )
        raise ConsistencyException(err_str)

    if set(RESERVED_PORTS).issubset(forward_ports):
        err_str = 'forwarding reserved port. reserved ports: {}'.format(RESERVED_PORTS)
        raise ConsistencyException(err_str)


def assert_python_versions_consistent() -> None:
    dockerfile_python_version_from_statement_re = re.compile(r'^FROM python:([\.0-9]*).*')
    all_dockerfile_python_versions = _get_string_from_file(
        match_object=dockerfile_python_version_from_statement_re,
        file_path=DOCKERFILE_FILE_PATH,
        expect_unique_match=False,
    )
    if len(set(all_dockerfile_python_versions)) != 1:
        err_str = 'found inconsistent python versions referenced in Dockerfiles: {}'.format(
            all_dockerfile_python_versions)
        raise ConsistencyException(err_str)

    unique_dockerfile_python_version = all_dockerfile_python_versions[0]
    poetry_python_version_re = re.compile(r'python[^0-9]*([\.0-9]*)')
    poetry_python_version = _get_string_from_file(
        match_object=poetry_python_version_re,
        file_path=POETRY_TOML_FILE_PATH,
        expect_unique_match=True,
    )[0]
    if poetry_python_version != unique_dockerfile_python_version:
        err_str = 'python version in Dockerfile = {}. does not match version {} in {}'.format(
            unique_dockerfile_python_version,
            poetry_python_version,
            POETRY_TOML_FILE_PATH,
        )
        raise ConsistencyException(err_str)


if __name__ == '__main__':
    assert_flask_app_names_correct()
    assert_all_files_windows_compatible()
    assert_port_values_consistent()
    assert_python_versions_consistent()
