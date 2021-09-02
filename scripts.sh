#!/bin/bash
# set app name. change this, and only this, to localize to new app
APP_NAME=python_base
# get paramaeters passed by user
SCRIPT_ACTION_ARG=$1
APP_NAME_ARG=$2
# retreive absolute path and directory
ABSOLUTE_PATH=$(pwd)
CONTAINING_DIR="$(basename ${ABSOLUTE_PATH})"
# set image names relative to app names
BASE_IMAGE_NAME=base_image
DEV_IMAGE_NAME=${APP_NAME}_dev
PROD_IMAGE_NAME=${APP_NAME}_prod
# set default port to use for app
PORT=5000

function find_and_replace_line_in_file() {
    RegularExpression=$1
    ReplacementString=$2
    TargetFile=$3
    MatchCount=$(grep "${RegularExpression}" ${TargetFile} | wc -l)
    if [ $MatchCount -eq 0 ]; then
        printf 'ERROR! Found %i matches for: %-30s file: %s\n' "${MatchCount}" "${RegularExpression}" "${TargetFile}"
    elif [ $MatchCount -gt 1 ]; then
        printf 'ERROR! Found %i matches for: %-30s file: %s\n' "${MatchCount}" "${RegularExpression}" "${TargetFile}"
    else
        sed -i "" "s/$RegularExpression/$ReplacementString/" $TargetFile
        printf 'replaced string: %-30s file: %s\n' "${ReplacementString}" "${TargetFile}"
    fi
}

function build_image_base() {
    docker build \
    --tag ${BASE_IMAGE_NAME}:latest \
    --file docker/Dockerfile.base .
}
function build_image_dev() {
    docker build \
    --tag ${DEV_IMAGE_NAME}:latest \
    --file docker/Dockerfile.dev .
}

function build_image_prod() {
    docker build \
    --tag ${PROD_IMAGE_NAME}:latest \
    --file docker/Dockerfile.prod .
}

if [ "$SCRIPT_ACTION_ARG" = "--build-image-dev" ]; then
    build_image_base && \
    build_image_dev
elif [ "$SCRIPT_ACTION_ARG" = "--build-image-prod" ]; then
    build_image_base && \
    build_image_prod
elif [ "$SCRIPT_ACTION_ARG" = "--build-image" ]; then
    build_image_base && \
    build_image_prod && \
    build_image_dev
elif [ "$SCRIPT_ACTION_ARG" = "--clean-docker" ]; then
    docker system prune
elif [ "$SCRIPT_ACTION_ARG" = "--enter-container-dev" ]; then
    docker run \
    -it \
    --rm \
    --entrypoint="" \
    --workdir=/app \
    --env PYTHONPATH=/app \
    --volume ${ABSOLUTE_PATH}:/app \
    --publish ${PORT}:${PORT} \
    ${DEV_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$SCRIPT_ACTION_ARG" = "--enter-container-prod" ]; then
    docker run \
    -it \
    --rm \
    --entrypoint="" \
    --workdir=/app \
    --publish ${PORT}:${PORT} \
    ${PROD_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$SCRIPT_ACTION_ARG" = "--run-prod" ]; then
    docker run \
    --publish ${PORT}:${PORT} \
    ${PROD_IMAGE_NAME}:latest
elif [ "$SCRIPT_ACTION_ARG" = "--set-app-name" ]; then
    if [ -z "$APP_NAME_ARG" ]; then
        printf "must pass app name as second arg\n"
        exit 1
    fi
    RegularExpression="^APP_NAME[ ]*=.*"
    ReplacementString="APP_NAME=${APP_NAME_ARG}"
    TargetFile="scripts.sh"
    find_and_replace_line_in_file "$RegularExpression" "$ReplacementString" "$TargetFile"

    RegularExpression="^name[ ]*=[ ]*\".*\""
    ReplacementString="name = \"${APP_NAME_ARG}\""
    TargetFile="pyproject.toml"
    find_and_replace_line_in_file "$RegularExpression" "$ReplacementString" "$TargetFile"

    RegularExpression="\"image\":[ ]*\".*\"[ ]*,"
    ReplacementString="\"image\": \"${APP_NAME_ARG}_dev:latest\","
    TargetFile=".devcontainer/devcontainer.json"
    find_and_replace_line_in_file "$RegularExpression" "$ReplacementString" "$TargetFile"
else
    printf "action ${SCRIPT_ACTION_ARG} not found\n"
fi
