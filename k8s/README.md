# Kubernetes (k8s)
This repo can be deployed to a k8s cluster locally or in Google Cloud through a series of k8s yaml files.
K8s yaml files must be coordinated with other variables in the codebase (EG: container names) which may contain sensitive information.
We work with a series of k8s yaml template files that must be "rendered" to specific and usable k8s yaml files.

Each template is named `X-template.yml`.
Each template must be "rendered" by performing a variable replacement.
This rendering is done with `k8s_render_tempalte.py`, passing a `--file_name` matching a template, and various required variables.
EG:
```
python k8s_render_tempalte.py --file_name=python-api-template.yml --GCLOUD_PROD_IMAGE_NAME=${GCLOUD_PROD_IMAGE_NAME}
```

Rendering is handled automatically when issuing make commands.