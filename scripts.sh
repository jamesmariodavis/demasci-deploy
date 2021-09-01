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
DEV_IMAGE_NAME=${APP_NAME}_dev
PROD_IMAGE_NAME=${APP_NAME}_prod

function update_line_in_file() {
    BRE=$1
    REPLACE_STRING=$2
    REPLACE_FILE=$3
    NUM_MATCHES=$(grep "${BRE}" ${REPLACE_FILE} | wc -l)
    if [ $NUM_MATCHES -eq 0 ]; then
        printf 'ERROR! Found %i matches for: %-30s file: %s\n' "${NUM_MATCHES}" "${BRE}" "${REPLACE_FILE}"
    elif [ $NUM_MATCHES -gt 1 ]; then
        printf 'ERROR! Found %i matches for: %-30s file: %s\n' "${NUM_MATCHES}" "${BRE}" "${REPLACE_FILE}"
    else
        sed -i "" "s/$BRE/$REPLACE_STRING/" $REPLACE_FILE
        printf 'replaced string: %-30s file: %s\n' "${REPLACE_STRING}" "${REPLACE_FILE}"
    fi
}

if [ "$SCRIPT_ACTION_ARG" = "--build-image-dev" ]; then
    docker build \
    --tag ${DEV_IMAGE_NAME}:latest \
    --file docker/Dockerfile.dev .
elif [ "$SCRIPT_ACTION_ARG" = "--build-image-prod" ]; then
    docker build \
    --tag ${PROD_IMAGE_NAME}:latest \
    --file docker/Dockerfile.prod .
elif [ "$SCRIPT_ACTION_ARG" = "--enter-container-dev" ]; then
    docker run \
    -it \
    --entrypoint="" \
    --rm \
    --net=host \
    --workdir=/app \
    --env PYTHONPATH=/app \
    --volume ${ABSOLUTE_PATH}:/app \
    ${DEV_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$SCRIPT_ACTION_ARG" = "--enter-container-prod" ]; then
    docker run -it \
    --entrypoint="" \
    --rm \
    --net=host \
    --workdir=/app \
    ${PROD_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$SCRIPT_ACTION_ARG" = "--set-app-name" ]; then
    if [ -z "$APP_NAME_ARG" ]; then
        printf "must pass app name as second arg\n"
        exit 1
    fi
    BRE="^\$APP_NAME[ ]*=[ ]*\".*\""
    REPLACE_STRING="\$APP_NAME=\"${APP_NAME_ARG}\""
    REPLACE_FILE="scripts.ps1"
    update_line_in_file "$BRE" "$REPLACE_STRING" "$REPLACE_FILE"

    BRE="^APP_NAME[ ]*=.*"
    REPLACE_STRING="APP_NAME=${APP_NAME_ARG}"
    REPLACE_FILE="scripts.sh"
    update_line_in_file "$BRE" "$REPLACE_STRING" "$REPLACE_FILE"

    BRE="^name[ ]*=[ ]*\".*\""
    REPLACE_STRING="name = \"${APP_NAME_ARG}\""
    REPLACE_FILE="pyproject.toml"
    update_line_in_file "$BRE" "$REPLACE_STRING" "$REPLACE_FILE"

    BRE="\"image\":[ ]*\".*\"[ ]*,"
    REPLACE_STRING="\"image\": \"${APP_NAME_ARG}_dev:latest\","
    REPLACE_FILE=".devcontainer/devcontainer.json"
    update_line_in_file "$BRE" "$REPLACE_STRING" "$REPLACE_FILE"
else
    printf "action ${SCRIPT_ACTION_ARG} not found\n"
fi
