#!/bin/bash

ABSOLUTE_FILE_PATH=$(dirname "$(realpath $0)")
source ${ABSOLUTE_FILE_PATH}/../configure.sh

# PORT is defined in image or injected
uvicorn ${API_MODULE_LOCATION}:${API_APP_NAME_IN_CODE} --host 0.0.0.0 --port ${PORT}