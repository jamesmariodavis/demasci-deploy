#!/bin/bash

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

###################
# setup flask app #
###################
# configure gunicorn server. used to configure gunicorn commands
# set APP_LOCATION to main entrypoint for flask app
FLASK_APP_MODULE_LOCATION=flask_app
# set APP_METHOD_NAME to name of application defined in python
FLASK_APP_NAME_IN_CODE=app
# use default flask port 5000
FLASK_APP_PORT=5000
# set workers to number of cpu cores
FLASK_APP_WORKERS=1
FLASK_APP_THREADS=8
# timeout is set to 0 to disable the timeouts of the workers to allow Google Cloud Run to handle instance scaling
FLASK_APP_TIMEOUT=0

##########################
# choose coin-or solvers #
##########################
# use y or n for each variable
INCLUDE_CBC=y

# all builds use the same args
DOCKER_BUILD_WITH_ARGS="docker build \
    --build-arg FLASK_APP_MODULE_LOCATION_ARG=${FLASK_APP_MODULE_LOCATION} \
    --build-arg FLASK_APP_NAME_IN_CODE_ARG=${FLASK_APP_NAME_IN_CODE} \
    --build-arg FLASK_APP_PORT_ARG=${FLASK_APP_PORT} \
    --build-arg FLASK_APP_WORKERS_ARG=${FLASK_APP_WORKERS} \
    --build-arg FLASK_APP_THREADS_ARG=${FLASK_APP_THREADS} \
    --build-arg FLASK_APP_TIMEOUT_ARG=${FLASK_APP_TIMEOUT} \
    --build-arg BASE_IMAGE_NAME_ARG=${BASE_IMAGE_NAME}:latest"


function build_image_base() {
    docker build \
    --tag ${BASE_IMAGE_NAME}:latest \
    --build-arg INCLUDE_CBC=${INCLUDE_CBC} \
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
elif [ "$1" = "--clean-docker" ]; then
    docker system prune $2
elif [ "$1" = "--enter-dev" ]; then
    docker run \
    -it \
    --rm \
    --entrypoint="" \
    --workdir=/app \
    --env PYTHONPATH=/app \
    --volume ${ABSOLUTE_PATH}:/app \
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
    --entrypoint="" \
    --workdir=/app \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    --name="${PROD_IMAGE_NAME}-bash" \
    ${PROD_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$1" = "--run-prod" ]; then
    # mimics what happens on deploy
    docker run \
    --publish ${FLASK_APP_PORT}:${FLASK_APP_PORT} \
    ${PROD_IMAGE_NAME}:latest
else
printf "action ${1} not found\n"
fi
