from typing import Dict
import argparse
import os
from app_lib.app_paths import K8S_DIR


def _replace_variables_with_args(
    original_str: str,
    replacement_dict: Dict[str, str],
) -> str:
    new_str = original_str
    for key, value in replacement_dict.items():
        replacement_expression = '{{' + key + '}}'
        new_str = new_str.replace(replacement_expression, value)
    return new_str


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_name')
    parser.add_argument('--GCLOUD_PROD_IMAGE_NAME')
    args = parser.parse_args()

    template_file_name = args.file_name
    file_path = os.path.join(K8S_DIR, template_file_name)
    print('Processing file {} ...'.format(file_path))
    with open(file_path, 'r', encoding='utf8') as f:
        yml_template_str = f.read()

    k8s_replacement_dict = {
        'GCLOUD_PROD_IMAGE_NAME': args.GCLOUD_PROD_IMAGE_NAME,
    }
    print('Using variables {} ...'.format(k8s_replacement_dict))
    rendered_yml_str = _replace_variables_with_args(
        original_str=yml_template_str,
        replacement_dict=k8s_replacement_dict,
    )
    rendered_file_name = template_file_name.split('-template')[0] + '-rendered.yml'
    rendered_file_path = os.path.join(K8S_DIR, rendered_file_name)

    with open(rendered_file_path, 'w', encoding='utf8') as f:
        f.write(rendered_yml_str)
