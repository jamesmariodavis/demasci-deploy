# tests that repo conforms to expectations
import os
import re
import subprocess
import json5
from app_lib.app_paths import ROOT_DIR
from app_lib import FileParsingHelpers


class ConsistencyException(Exception):
    pass


RESERVED_PORTS = (
    8001,  # k8s dashboard
    5001,  # k8s uvicorn port defined in k8s/uvicorn.yml
)

CONFIGURE_FILE_PATH = os.path.join(ROOT_DIR, 'configure.sh')
MAKEFILE_FILE_PATH = os.path.join(ROOT_DIR, 'Makefile')
GITIGNORE_FILE_PATH = os.path.join(ROOT_DIR, '.gitignore')
DOCKERIGNORE_FILE_PATH = os.path.join(ROOT_DIR, '.dockerignore')
DEVCONTAINER_JSON_FILE_PATH = os.path.join(ROOT_DIR, '.devcontainer', 'devcontainer.json')
POETRY_TOML_FILE_PATH = os.path.join(ROOT_DIR, 'pyproject.toml')
DOCKERFILE_FILE_PATH = os.path.join(ROOT_DIR, 'docker', 'Dockerfile')
K8S_APP_YML_FILE_PATH = os.path.join(ROOT_DIR, 'k8s', 'python-api.yml')

with open(DEVCONTAINER_JSON_FILE_PATH, 'r', encoding='utf8') as devcontainer_file:
    DEVCONTAINER_JSON = json5.load(devcontainer_file)

# k8s yaml is not a true yaml because it specifies multiple resources
K8S_YAML_LIST = FileParsingHelpers.get_k8s_yaml_list(file_path=K8S_APP_YML_FILE_PATH)


def assert_all_files_windows_compatible() -> None:
    std_out_str = subprocess.check_output("git ls-files", shell=True)
    all_files = std_out_str.decode('utf8').split('\n')
    windows_incompatible_files = [file for file in all_files if re.compile(r'.*[:<>"\|\?\*\\].*').match(file)]
    if windows_incompatible_files:
        err_str = 'found files incompatible with windows naming scheme: {}'.format(windows_incompatible_files)
        raise ConsistencyException(err_str)


def assert_containers_coordinate() -> None:
    terminal_command = '. {} && echo $DEV_IMAGE_NAME'.format(CONFIGURE_FILE_PATH)
    std_out_str = subprocess.check_output(terminal_command, shell=True)
    dev_image_name = std_out_str.decode('utf8').split('\n', maxsplit=1)[0]

    terminal_command = 'make --no-print-directory get-gcloud-prod-image-name'
    std_out_str = subprocess.check_output(terminal_command, shell=True)
    gcloud_prod_image_name = std_out_str.decode('utf8').split('\n', maxsplit=1)[0]

    vscode_dev_image_ref = DEVCONTAINER_JSON['image']
    if dev_image_name != vscode_dev_image_ref:
        err_str = 'dev image name: {} vscode referenced image does not match: {}'.format(
            dev_image_name,
            vscode_dev_image_ref,
        )
        raise ConsistencyException(err_str)

    k8s_api_deploy_yml = K8S_YAML_LIST[0]
    k8s_image_ref = k8s_api_deploy_yml['spec']['template']['spec']['containers'][0]['image']
    if gcloud_prod_image_name != k8s_image_ref:
        err_str = 'gcloud prod image: {} k8s referenced image does not match: {}'.format(
            gcloud_prod_image_name,
            k8s_image_ref,
        )
        raise ConsistencyException(err_str)


def assert_app_api_names_correct() -> None:
    # retreive referenced module for api server
    configured_api_module_name_re = re.compile(r'^API_MODULE_LOCATION[]*=[]*(.*)')
    try:
        configured_api_module_name = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=configured_api_module_name_re,
            file_path=CONFIGURE_FILE_PATH,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            CONFIGURE_FILE_PATH,
            configured_api_module_name_re.pattern,
        )
        raise ConsistencyException(err_str) from e
    infered_python_file = '{}.py'.format(configured_api_module_name)
    infered_python_file_path = os.path.join(ROOT_DIR, infered_python_file)

    # check if referenced module exists
    if not os.path.exists(infered_python_file_path):
        err_str = '{} references flask module {}. does not exist'.format(
            CONFIGURE_FILE_PATH,
            infered_python_file,
        )
        raise ConsistencyException(err_str)

    # retreive referenced api app name
    configured_api_app_name_re = re.compile(r'^API_APP_NAME_IN_CODE[ ]*=[ ]*(.*)')
    try:
        configured_api_app_name = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=configured_api_app_name_re,
            file_path=CONFIGURE_FILE_PATH,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            CONFIGURE_FILE_PATH,
            configured_api_app_name_re.pattern,
        )
        raise ConsistencyException(err_str) from e

    # retreive actual api app name
    python_api_app_name_re = re.compile(r'(.*) = FastAPI\(\).*')
    try:
        python_api_app_name = FileParsingHelpers.get_pattern_matches_from_file(
            match_object=python_api_app_name_re,
            file_path=infered_python_file_path,
            expect_unique_match=True,
        )[0]
    except ConsistencyException as e:
        err_str = '{} does not have proper flask app configuration. expected unique match for {}'.format(
            infered_python_file_path,
            python_api_app_name_re.pattern,
        )
        raise ConsistencyException(err_str) from e

    # verify same name
    if configured_api_app_name != python_api_app_name:
        err_str = 'flask app names inconsistent. Dockerfile reference: {}. Flask app name: {}.'.format(
            configured_api_app_name,
            python_api_app_name,
        )
        raise ConsistencyException(err_str)


def assert_port_values_consistent() -> None:
    forward_ports = DEVCONTAINER_JSON['forwardPorts']
    vscode_injected_port_env_var = int(DEVCONTAINER_JSON['containerEnv']['PORT'])

    ray_dashboard_port_re = re.compile(r'^RAY_DASHBOARD_PORT[ ]*=[ ]*(.*)')
    api_test_port_re = re.compile(r'^API_TEST_PORT[ ]*=[ ]*(.*)')

    ray_dashboard_port = FileParsingHelpers.get_pattern_matches_from_file(
        match_object=ray_dashboard_port_re,
        file_path=CONFIGURE_FILE_PATH,
        expect_unique_match=True,
    )[0]
    api_test_port = FileParsingHelpers.get_pattern_matches_from_file(
        match_object=api_test_port_re,
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
    all_dockerfile_python_versions = FileParsingHelpers.get_pattern_matches_from_file(
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
    poetry_python_version = FileParsingHelpers.get_pattern_matches_from_file(
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


def assert_secrets_ignored() -> None:
    gcloud_secret_file_re = re.compile(r'^GCLOUD_SERVICE_ACCOUNT_KEY_FILE[ ]*=[ ]*(.*)')
    gcloud_secret_file_name = FileParsingHelpers.get_pattern_matches_from_file(
        match_object=gcloud_secret_file_re,
        file_path=CONFIGURE_FILE_PATH,
        expect_unique_match=True,
    )[0]
    gcloud_secret_file_name = gcloud_secret_file_name.replace('\'', '').replace('"', '')

    # check that this file is ignored by docker and git
    # make empty group at end
    match_string = '^{}([ ]*)'.format(gcloud_secret_file_name)
    gcloud_secret_in_ignore_match_object = re.compile(match_string)
    # just check that there is a unique match
    _ = FileParsingHelpers.get_pattern_matches_from_file(
        match_object=gcloud_secret_in_ignore_match_object,
        file_path=GITIGNORE_FILE_PATH,
        expect_unique_match=True,
    )
    _ = FileParsingHelpers.get_pattern_matches_from_file(
        match_object=gcloud_secret_in_ignore_match_object,
        file_path=DOCKERIGNORE_FILE_PATH,
        expect_unique_match=True,
    )


if __name__ == '__main__':
    assert_app_api_names_correct()
    assert_all_files_windows_compatible()
    assert_port_values_consistent()
    assert_python_versions_consistent()
    assert_secrets_ignored()
    assert_containers_coordinate()
