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
BASE_IMAGE_NAME=${INFERED_REPO_NAME}-base
DEV_IMAGE_NAME=${INFERED_REPO_NAME}-dev
PROD_IMAGE_NAME=${INFERED_REPO_NAME}-prod

# all builds use the same args
DOCKER_BUILD_WITH_ARGS="docker build \
    --build-arg FLASK_APP_MODULE_LOCATION_ARG=${FLASK_APP_MODULE_LOCATION} \
    --build-arg FLASK_APP_NAME_IN_CODE_ARG=${FLASK_APP_NAME_IN_CODE} \
    --build-arg FLASK_APP_PORT_ARG=${FLASK_APP_PORT} \
    --build-arg FLASK_APP_WORKERS_ARG=${FLASK_APP_WORKERS} \
    --build-arg FLASK_APP_THREADS_ARG=${FLASK_APP_THREADS} \
    --build-arg FLASK_APP_TIMEOUT_ARG=${FLASK_APP_TIMEOUT} \
    --build-arg INCLUDE_CBC=${INCLUDE_CBC} \
    --build-arg GCLOUD_PROJECT_ID_ARG=${GCLOUD_PROJECT_ID} \
    --build-arg GCLOUD_REGION_ARG=${GCLOUD_REGION} \
    --build-arg GCLOUD_SERVICE_NAME_ARG=${GCLOUD_SERVICE_NAME} \
    --build-arg GCLOUD_ALLOW_UNAUTHENTICATED_PARAM_ARG=${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} \
    --build-arg PROD_IMAGE_NAME_ARG=${PROD_IMAGE_NAME}:latest \
    --build-arg BASE_IMAGE_NAME_ARG=${BASE_IMAGE_NAME}:latest"


function build_image_base() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${BASE_IMAGE_NAME}:latest \
    --file docker/Dockerfile.base .
}
function build_image_dev() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${DEV_IMAGE_NAME}:latest \
    --file docker/Dockerfile.dev .
}

function build_image_prod() {
    ${DOCKER_BUILD_WITH_ARGS} \
    --tag ${PROD_IMAGE_NAME}:latest \
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
elif [ "$1" = "--build" ]; then
    # build all images in order
    build_image_base && \
    build_image_prod && \
    build_image_dev && \
    docker image prune --force
elif [ "$1" = "--build-prod" ]; then
    build_image_base && \
    build_image_prod && \
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
    --env PYTHONPATH=/app \
    --volume ${ABSOLUTE_PATH}:/app \
    --volume //var/run/docker.sock:/var/run/docker.sock \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    --name="${DEV_IMAGE_NAME}-bash" \
    ${DEV_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$1" = "--enter-prod" ]; then
    # similar to entering dev container
    # does not mount top directory of repo
    # using copied version of repo (from build) located in /app in container
    docker run \
    -it \
    --rm \
    --env PORT=${FLASK_APP_PORT} \
    --entrypoint="" \
    --workdir=/app \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    --name="${PROD_IMAGE_NAME}-bash" \
    ${PROD_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$1" = "--run" ]; then
    # mimics what happens on deploy
    docker run \
    --env PORT=${FLASK_APP_PORT} \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    ${PROD_IMAGE_NAME}:latest
else
    printf "action ${1} not found\n"
fi
