# set app name. change this, and only this, to localize to new app
$APP_NAME="python_base"
# get paramaeters passed by user
$SCRIPT_ACTION_ARG=$args[0]
$APP_NAME_ARG=$args[1]
# retreive absolute path
$ABSOLUTE_PATH=Get-Location
# set image names relative to app name
$DEV_IMAGE_NAME="${APP_NAME}_dev"
$PROD_IMAGE_NAME="${APP_NAME}_prod"
function Find-And-Replace-Line-In-File {
    param (
        [string]$RegularExpression,
        [string]$ReplacementString,
        [string]$TargetFile
    )
    $LineMatches=Select-String -Pattern $RegularExpression -Path $TargetFile
    [int]$MatchCount=$LineMatches.Count
    $ErrorString='ERROR! Found {0} matches for: {1} file: {2}' -f $MatchCount, $RegularExpression.PadRight(30,' '), $TargetFile
    if ($MatchCount -eq 0) {
        Write-Output $ErrorString
    }
    elseif ($MatchCount -gt 1) {
        Write-Output $ErrorString
    }
    else {
        (Get-Content $TargetFile) -replace $RegularExpression, $ReplacementString | Set-Content $TargetFile
        $SuccessString='replaced string: {0} file: {1}' -f $ReplacementString.PadRight(30,' '), $TargetFile
        Write-Output $SuccessString
    }
}

if ($SCRIPT_ACTION_ARG -eq '--build-image-dev'){
    Invoke-Command -ScriptBlock {
        docker build `
        --tag ${DEV_IMAGE_NAME}:latest `
        --file docker/Dockerfile.dev .
    }
}
elseif ($SCRIPT_ACTION_ARG -eq '--build-image-prod') {
    Invoke-Command -ScriptBlock {
        docker build `
        --tag ${PROD_IMAGE_NAME}:latest `
        --file docker/Dockerfile.prod .
    }
}
elseif ($SCRIPT_ACTION_ARG -eq "--enter-container-dev") {
    Invoke-Command -ScriptBlock {
        docker run -it `
        --entrypoint="" `
        --rm `
        --net=host `
        --workdir=/app `
	    --env PYTHONPATH=/app `
        --volume ${ABSOLUTE_PATH}:/app `
        ${DEV_IMAGE_NAME}:latest `
        /bin/bash
    }
}
elseif ($SCRIPT_ACTION_ARG -eq "--enter-container-prod") {
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
elseif ($SCRIPT_ACTION_ARG -eq "--set-app-name") {
    if (!$APP_NAME_ARG) {
        Write-Output "must pass app name as second arg"
        exit 1
    }
    $RegularExpression="APP_NAME[ ]*=[ ]*`".*`""
    $ReplacementString="APP_NAME=`"${APP_NAME_ARG}`""
    $TargetFile="scripts.ps1"
    Replace-Line-In-File -RegularExpression $RegularExpression -ReplacementString $ReplacementString -TargetFile $TargetFile

    $RegularExpression="^APP_NAME[ ]*=.*"
    $ReplacementString="APP_NAME=${APP_NAME_ARG}"
    $TargetFile="scripts.sh"
    Replace-Line-In-File -RegularExpression $RegularExpression -ReplacementString $ReplacementString -TargetFile $TargetFile

    $RegularExpression="^name[ ]*=[ ]*`".*`""
    $ReplacementString="name = `"${APP_NAME_ARG}`""
    $TargetFile="pyproject.toml"
    Replace-Line-In-File -RegularExpression $RegularExpression -ReplacementString $ReplacementString -TargetFile $TargetFile

    $RegularExpression="`"image`":[ ]*`".*`"[ ]*,"
    $ReplacementString="`"image`": `"${APP_NAME_ARG}_dev:latest`","
    $TargetFile=".devcontainer/devcontainer.json"
    Replace-Line-In-File -RegularExpression $RegularExpression -ReplacementString $ReplacementString -TargetFile $TargetFile
}
else {
    Write-Output "action ${SCRIPT_ACTION_ARG} not found"
}
