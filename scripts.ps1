# set app name. change this, and only this, to localize to new app
$APP_NAME="python_base"
# get paramaeters passed by user
$PASSED_PARAMETER=$args[0]
# retreive absolute path
$ABSOLUTE_PATH=Get-Location
# set image names relative to app name
$DEV_IMAGE_NAME="${APP_NAME}_dev"
$PROD_IMAGE_NAME="${APP_NAME}_prod"


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
else {
    Write-Output "option ${PASSED_PARAMETER} not found"
}