#!/bin/bash

# retreive configuration
source configure.sh

RELATIVE_PATH=$(pwd)

# all builds use the same args
DOCKER_BUILD_WITH_ARGS="docker build \
    --build-arg DOCKER_CODE_MOUNT_DIRECTORY_ARG=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --build-arg FLASK_APP_PORT_ARG=${FLASK_APP_PORT} \
    --build-arg GCLOUD_PROJECT_ID_ARG=${GCLOUD_PROJECT_ID} \
    --build-arg GCLOUD_REGION_ARG=${GCLOUD_REGION} \
    --build-arg GCLOUD_SERVICE_ACCOUNT_KEY_FILE_ARG=${GCLOUD_SERVICE_ACCOUNT_KEY_FILE} \
    "

function build_image_base() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${BASE_IMAGE_NAME} \
    --target 'base-image' \
    --file docker/Dockerfile .
}

function build_image_dev() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${DEV_IMAGE_NAME} \
    --target 'dev-image' \
    --file docker/Dockerfile .
}

function build_image_prod() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${PROD_IMAGE_NAME} \
    --target 'prod-image' \
    --file docker/Dockerfile .
}

if [ "$1" = "--help" ]; then
    PadSpace=20
    printf "available commands:\n"
    printf "%-${PadSpace}s builds all Docker images required for development and production\n" "--build"
    printf "%-${PadSpace}s deletes unused containers and images. use -a to delete all\n" "--clean-docker"
    printf "%-${PadSpace}s enters development container and starts interactive bash shell\n" "--enter-dev"
    printf "%-${PadSpace}s enters production container and starts interactive bash shell\n" "--enter-prod"
    printf "%-${PadSpace}s starts production container to simulate deployment\n" "--run-prod"
elif [ "$1" = "--build" ]; then
    build_image_prod \
    && build_image_dev \
    && docker image prune --force
elif [ "$1" = "--build-prod" ]; then
    build_image_base \
    && docker image prune --force
elif [ "$1" = "--clean-docker" ]; then
    docker system prune $2
elif [ "$1" = "--enter-dev" ]; then
    docker run \
    -it \
    --rm \
    --entrypoint="" \
    --workdir=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --env PYTHONPATH=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --volume ${RELATIVE_PATH}:${DOCKER_CODE_MOUNT_DIRECTORY} \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --volume ~/.kube:/root/.kube \
    --publish ${API_TEST_PORT}:${API_TEST_PORT} \
    --publish ${RAY_DASHBOARD_PORT}:${RAY_DASHBOARD_PORT} \
    --name="${INFERED_REPO_NAME}-dev-bash" \
    ${DEV_IMAGE_NAME} \
    /bin/bash
elif [ "$1" = "--enter-prod" ]; then
    # similar to entering dev container
    # does not mount top directory of repo
    # only code copied during build is used
    # inject PORT env var to simulate production
    # see: https://cloud.google.com/run/docs/reference/container-contract
    docker run \
    -it \
    --rm \
    --env PORT=${FLASK_APP_PORT} \
    --entrypoint="" \
    --workdir=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --publish ${API_TEST_PORT}:${API_TEST_PORT} \
    --name="${INFERED_REPO_NAME}-prod-bash" \
    ${PROD_IMAGE_NAME} \
    /bin/bash
elif [ "$1" = "--run" ]; then
    # mimics what happens on deploy
    # inject PORT env var to simulate production
    # see: https://cloud.google.com/run/docs/reference/container-contract
    docker run \
    --rm \
    --env PORT=${API_TEST_PORT} \
    --publish ${API_TEST_PORT}:${API_TEST_PORT} \
    --name="${INFERED_REPO_NAME}-prod-run" \
    ${PROD_IMAGE_NAME}
elif [ "$1" = "--k8s-proxy" ]; then
    # creates proxy to k8s cluster making it accsible on local machine
    echo "K8s Dashboard: http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/" \
    && kubectl proxy \
else
    printf "action ${1} not found\n"
fi
