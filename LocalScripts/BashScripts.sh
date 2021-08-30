# set app name. change this, and only this, to localize to new app
APP_NAME=python_base
# get paramaeters passed by user
PASSED_PARAMETER=$1
# retreive absolute path
ABSOLUTE_PATH=$(pwd)
# set image names relative to app names
DEV_IMAGE_NAME=${APP_NAME}_dev
PROD_IMAGE_NAME=${APP_NAME}_prod

echo $ABSOLUTE_PATH
if [ "$PASSED_PARAMETER" = "build-dev-image" ]; then
    docker build \
    --tag ${DEV_IMAGE_NAME}:latest \
    --file docker/Dockerfile.dev .
elif [ "$PASSED_PARAMETER" = "build-prod-image" ]; then
    docker build \
    --tag ${PROD_IMAGE_NAME}:latest \
    --file docker/Dockerfile.prod .
elif [ "$PASSED_PARAMETER" = "enter-dev-container" ]; then
    docker run \
    -it \
    --entrypoint="" \
    --rm \
    --net=host \
    --workdir=/${APP_NAME} \
    --env PYTHONPATH=${APP_NAME} \
    --volume ${ABSOLUTE_PATH}:/${APP_NAME} \
    ${DEV_IMAGE_NAME}:latest \
    /bin/bash
elif [ "$PASSED_PARAMETER" = "enter-prod-container" ]; then
    docker run -it \
    --entrypoint="" \
    --rm \
    --net=host \
    --workdir=/app \
    ${PROD_IMAGE_NAME}:latest \
    /bin/bash
else
    echo "option ${PASSED_PARAMETER} not found"
fi