######################################################
# Note: rebuild dev image after configuration update #
######################################################

######################
# gcloud identifiers #
######################

# project ID can be found on project page in gcp UI
GCLOUD_PROJECT_ID=python-base-325119

# choose nearby region https://cloud.google.com/compute/docs/regions-zones
GCLOUD_REGION=us-west1

# service name affects name of resource in gcp
GCLOUD_SERVICE_NAME=gcloud-flask-app

# parameter passed to toggle if app is public
# from https://cloud.google.com/sdk/gcloud/reference/run/deploy :
#
# --[no-]allow-unauthenticated
# Whether to enable allowing unauthenticated access to the service.
# This may take a few moments to take effect.
# Use --allow-unauthenticated to enable and --no-allow-unauthenticated to disable.
GCLOUD_ALLOW_UNAUTHENTICATED_PARAM='--allow-unauthenticated'

# service account must be created in console
GCLOUD_SERVICE_ACCOUNT="admin-171@python-base-325119.iam.gserviceaccount.com"


###################
# setup flask app #
###################

# set APP_LOCATION to main entrypoint for flask app
FLASK_APP_MODULE_LOCATION=flask_app

# set APP_METHOD_NAME to name of application defined in python
FLASK_APP_NAME_IN_CODE=app

# use default flask port 5000 for development
# port is injected during deployment as PORT env var
# see: https://cloud.google.com/run/docs/reference/container-contract
# local container runs inject FLASK_APP_PORT to PORT env var
FLASK_APP_PORT=5000

# set workers to number of cpu cores
FLASK_APP_WORKERS=1
FLASK_APP_THREADS=8

# timeout is set to 0 to disable the timeouts of the workers to allow Google Cloud Run to handle instance scaling
FLASK_APP_TIMEOUT=0
