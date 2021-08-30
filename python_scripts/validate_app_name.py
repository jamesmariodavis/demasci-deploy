import os
import re

THIS_FILE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_DIRECTORY = os.path.join(THIS_FILE_PATH, os.pardir)

POWERSHELL_SCRIPT_FILE_PATH = os.path.join(ROOT_DIRECTORY ,'LocalScripts/PowerShellScripts.ps1')
BASH_SCRIPT_FILE_PATH = os.path.join(ROOT_DIRECTORY ,'LocalScripts/BashScripts.sh')
POETRY_TOML_FILE_PATH = os.path.join(ROOT_DIRECTORY ,'pyproject.toml')

def get_implied_app_name_in_file(
    file_path: str,
    line_number: int,
    line_match_object: re.Pattern
) -> str:
    with open(file_path, 'r') as f:
        lines = f.readlines()
        app_name_line = lines[line_number]
        # validate line is as expected
        match_object = line_match_object.match(app_name_line)
        if not match_object:
            err_str = 'Expected line {} in {} to match {}'.format(
                file_path,
                line_number,
                line_match_object.pattern,
                )
            raise Exception(err_str)
        implied_app_name = match_object.groups(0)[0]
    return implied_app_name

powershell_script_app_name = get_implied_app_name_in_file(
    file_path=POWERSHELL_SCRIPT_FILE_PATH,
    line_number=1,
    line_match_object=re.compile(r'\$APP_NAME="(.*)"\n')
)

bash_script_app_name = get_implied_app_name_in_file(
    file_path=BASH_SCRIPT_FILE_PATH,
    line_number=1,
    line_match_object=re.compile(r'APP_NAME=(.*)\n')
)

poetry_toml_app_name = get_implied_app_name_in_file(
    file_path=POETRY_TOML_FILE_PATH,
    line_number=1,
    line_match_object=re.compile(r'name = "(.*)"\n')
)

# validate that all implied app names are consistent
app_names = (
    powershell_script_app_name,
    bash_script_app_name,
    poetry_toml_app_name,
)

if len(set(app_names)) != 1:
    err_str = 'Found multiple inconsistent app names: {}. Check Readme for fixes'.format(app_names)
    raise Exception(err_str)
