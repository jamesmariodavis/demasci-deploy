#!/bin/bash

# retreive configuration
source configure.sh

# retreive absolute path and parent directory
# when running bash in WSL these will not behave as expected
ABSOLUTE_PATH=$(pwd)
PARENT_DIR="$(basename ${ABSOLUTE_PATH})"

# retreive repo name from git fetch location
GIT_FETCH_LOCATION=$(git remote show -n origin | grep Fetch | cut -d: -f2-)
INFERED_REPO_NAME=$(echo "${GIT_FETCH_LOCATION}" | sed -E "s/.*\/(.*).git/\1/")

# set image names relative to git repo name
# images are built in a tree
# to get prod image (base-builder -> base -> prod)
# to get dev image (base-builder -> base -> dev)
# base-builder takes significant time to build and should be rebuilt infrequently
BASE_BUILDER_IMAGE_NAME=${INFERED_REPO_NAME}-base-builder:latest
BASE_IMAGE_NAME=${INFERED_REPO_NAME}-base:latest
DEV_IMAGE_NAME=${INFERED_REPO_NAME}-dev:latest
PROD_IMAGE_NAME=${INFERED_REPO_NAME}-prod:latest

# set code mount direcotry when entering docker containers
DOCKER_CODE_MOUNT_DIRECTORY=/app

# all builds use the same args
DOCKER_BUILD_WITH_ARGS="docker build \
    --build-arg FLASK_APP_MODULE_LOCATION_ARG=${FLASK_APP_MODULE_LOCATION} \
    --build-arg FLASK_APP_NAME_IN_CODE_ARG=${FLASK_APP_NAME_IN_CODE} \
    --build-arg FLASK_APP_PORT_ARG=${FLASK_APP_PORT} \
    --build-arg FLASK_APP_WORKERS_ARG=${FLASK_APP_WORKERS} \
    --build-arg FLASK_APP_THREADS_ARG=${FLASK_APP_THREADS} \
    --build-arg FLASK_APP_TIMEOUT_ARG=${FLASK_APP_TIMEOUT} \
    --build-arg DOCKER_CODE_MOUNT_DIRECTORY_ARG=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --build-arg INCLUDE_CBC=${INCLUDE_CBC} \
    --build-arg GCLOUD_PROJECT_ID_ARG=${GCLOUD_PROJECT_ID} \
    --build-arg GCLOUD_REGION_ARG=${GCLOUD_REGION} \
    --build-arg GCLOUD_SERVICE_NAME_ARG=${GCLOUD_SERVICE_NAME} \
    --build-arg GCLOUD_ALLOW_UNAUTHENTICATED_PARAM_ARG=${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} \
    --build-arg GCLOUD_SERVICE_ACCOUNT_ARG=${GCLOUD_SERVICE_ACCOUNT} \
    --build-arg GCLOUD_APP_URL_ARG=${GCLOUD_APP_URL} \
    --build-arg PROD_IMAGE_NAME_ARG=${PROD_IMAGE_NAME} \
    --build-arg BASE_IMAGE_NAME_ARG=${BASE_IMAGE_NAME} \
    --build-arg BASE_BUILDER_IMAGE_NAME_ARG=${BASE_BUILDER_IMAGE_NAME} \
    "

function build_image_base_builder() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${BASE_BUILDER_IMAGE_NAME} \
    --file docker/Dockerfile.base-builder .
}

function build_image_base() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${BASE_IMAGE_NAME} \
    --file docker/Dockerfile.base .
}

function build_image_dev() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${DEV_IMAGE_NAME} \
    --file docker/Dockerfile.dev .
}

function build_image_prod() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${PROD_IMAGE_NAME} \
    --file docker/Dockerfile.prod .
}

if [ "$1" = "--help" ]; then
    PadSpace=20
    printf "available commands:\n"
    printf "%-${PadSpace}s builds all Docker images required for development and production\n" "--build"
    printf "%-${PadSpace}s deletes unused containers and images. use -a to delete all\n" "--clean-docker"
    printf "%-${PadSpace}s enters development container and starts interactive bash shell\n" "--enter-dev"
    printf "%-${PadSpace}s enters production container and starts interactive bash shell\n" "--enter-prod"
    printf "%-${PadSpace}s starts production container to simulate deployment\n" "--run-prod"
elif [ "$1" = "--build-all" ]; then
    # build all images in order
    build_image_base_builder &&
    build_image_base && \
    build_image_prod && \
    build_image_dev && \
    docker image prune --force
elif [ "$1" = "--build" ]; then
    echo "skipping base-builder ..." &&\
    build_image_base && \
    build_image_prod && \
    build_image_dev && \
    docker image prune --force
elif [ "$1" = "--build-prod" ]; then
    echo "skipping base-builder ..." &&\
    build_image_base && \
    build_image_prod && \
    docker image prune --force
elif [ "$1" = "--build-dev" ]; then
    echo "skipping base-builder ..." &&\
    build_image_base && \
    build_image_dev && \
    docker image prune --force
elif [ "$1" = "--clean-docker" ]; then
    docker system prune $2
elif [ "$1" = "--enter-dev" ]; then
    docker run \
    -it \
    --rm \
    --entrypoint="" \
    --env PORT=${FLASK_APP_PORT} \
    --workdir=/app \
    --env PYTHONPATH=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --volume ${ABSOLUTE_PATH}:${DOCKER_CODE_MOUNT_DIRECTORY} \
    --volume /var/run/docker.sock:/var/run/docker.sock \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
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
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    --name="${INFERED_REPO_NAME}-prod-bash" \
    ${PROD_IMAGE_NAME} \
    /bin/bash
elif [ "$1" = "--run" ]; then
    # mimics what happens on deploy
    # inject PORT env var to simulate production
    # see: https://cloud.google.com/run/docs/reference/container-contract
    docker run \
    --rm \
    --env PORT=${FLASK_APP_PORT} \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    --name="${INFERED_REPO_NAME}-prod-run" \
    ${PROD_IMAGE_NAME}
else
    printf "action ${1} not found\n"
fi
