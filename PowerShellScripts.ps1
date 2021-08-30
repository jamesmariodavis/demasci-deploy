# get paramaeters passed by user
$PASSED_PARAMETER=$args[0]
# setup constants
$APP_NAME="python_base"
$DEV_IMAGE_NAME="${APP_NAME}_dev"
$PROD_IMAGE_NAME="${APP_NAME}_prod"
# retreive absolute path
$ABSOLUTE_PATH=Get-Location


if ($PASSED_PARAMETER -eq 'build-dev-image'){
    Invoke-Command -ScriptBlock {
        docker build `
        --tag ${DEV_IMAGE_NAME}:latest `
        --file docker/Dockerfile.dev .
    }
}
elseif ($PASSED_PARAMETER -eq 'build-prod-image') {
    Invoke-Command -ScriptBlock {
        docker build `
        --tag ${PROD_IMAGE_NAME}:latest `
        --file docker/Dockerfile.prod .
    }
}
elseif ($PASSED_PARAMETER -eq "enter-dev-container") {
    Invoke-Command -ScriptBlock {
        docker run -it `
        --entrypoint="" `
        --rm `
        --net=host `
        --workdir=/${APP_NAME} `
	    --env PYTHONPATH=${APP_NAME} `
        --volume ${ABSOLUTE_PATH}:/${APP_NAME} `
        ${DEV_IMAGE_NAME}:latest `
        /bin/bash
    }
}
elseif ($PASSED_PARAMETER -eq "enter-prod-container") {
    Invoke-Command -ScriptBlock {
        docker run -it `
        --entrypoint="" `
        --rm `
        --net=host `
        --workdir=/app `
        ${PROD_IMAGE_NAME}:latest `
        /bin/bash
    }
}