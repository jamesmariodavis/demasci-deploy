#!/bin/bash
######################################################
# Note: rebuild dev image after configuration update #
######################################################

####################
# basic repo setup #
####################

# retreive repo name from git fetch location
# can be used for project name
GIT_FETCH_LOCATION=$(git remote show -n origin | grep Fetch | cut -d: -f2-)
INFERED_REPO_NAME=$(echo "${GIT_FETCH_LOCATION}" | sed -E "s/.*\/(.*).git/\1/")

# set project name. must be coordinated with devcontainer.json
PROJECT_NAME='python-app'

# set image names relative to git repo name
# images are built in a tree implicit in docker/Dockerfile
BASE_IMAGE_NAME=${PROJECT_NAME}-base:latest
DEV_IMAGE_NAME=${PROJECT_NAME}-dev:latest
PROD_IMAGE_NAME=${PROJECT_NAME}-prod:latest

# set code mount direcotry when entering docker containers
DOCKER_CODE_MOUNT_DIRECTORY=/app

# target test coverage
PYTEST_FAIL_UNDER_COVERAGE=50

######################
# gcloud identifiers #
######################

# project ID can be found on project page in gcp UI
GCLOUD_PROJECT_ID=python-base-325119

# choose nearby region https://cloud.google.com/compute/docs/regions-zones
GCLOUD_REGION=us-west1
GCLOUD_ZONE=us-west1-a

# service account must be created in web console
GCLOUD_SERVICE_ACCOUNT="admin-171@python-base-325119.iam.gserviceaccount.com"

# prod image name will create local tag and remote tag
GCLOUD_PROD_IMAGE_NAME=gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME}

# credentials for service account
# refer to README
GCLOUD_SERVICE_ACCOUNT_KEY_FILE='google_key.json'

# service name affects name of resource in Cloud Run
GCLOUD_SERVICE_NAME=python-app

# cluster name affects name of resource in k8s
GCLOUD_K8S_CLUSTER_NAME=python-app

# context is relevant for any command related to kubectl
# to see all contexts use `kubectl config get-contexts`
# gcloud generates name procedurally
GCLOUD_K8S_CONTEXT_NAME="gke_${GCLOUD_PROJECT_ID}_${GCLOUD_ZONE}_${GCLOUD_K8S_CLUSTER_NAME}"

# parameter passed to toggle if app is public
# from https://cloud.google.com/sdk/gcloud/reference/run/deploy :
#
# --[no-]allow-unauthenticated
# Whether to enable allowing unauthenticated access to the service.
# This may take a few moments to take effect.
# Use --allow-unauthenticated to enable and --no-allow-unauthenticated to disable.
GCLOUD_ALLOW_UNAUTHENTICATED_PARAM='--allow-unauthenticated'

#############
# setup api #
#############

# set APP_MODULE to main entrypoint for api
# corresponds to file name in root directory
# EG: API_MODULE_LOCATION=api => api.py is the target file
# EG: API_MODULE_LOCATION=lib/api => lib/api.py is the target file
API_MODULE_LOCATION=api

# set API_APP_NAME_IN_CODE to name of application defined in python
API_APP_NAME_IN_CODE=app

# port bound by uvicorn is injected as PORT env var
# see: https://cloud.google.com/run/docs/reference/container-contract for cloud run use case
# see k8s/uvicorn.yml for k8s use case
# see scripts.sh for local container use case
# see .devcontainer/devcontainer.json for vscode use case
# API_TEST_PORT referenced in scripts.sh for local development case
API_TEST_PORT=5000

#############
# setup ray #
#############

RAY_DASHBOARD_PORT=8265

#############
# setup k8s #
#############

# see here: https://github.com/kubernetes/dashboard
K8S_DASHBOARD_VERSION=2.3.1

# local context for deploying to local cluster
# set by installing application (docker-desktop)
K8S_LOCAL_CONTEXT_NAME=docker-desktop