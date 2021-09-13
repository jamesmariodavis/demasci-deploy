ABSOLUTE_PATH=$(abspath .)
GCLOUD_IDENTITY_TOKEN=$(shell gcloud auth print-identity-token)
PYTEST_FAIL_UNDER_COVERAGE=50

#########
# Tests #
#########
.PHONY: test-consistency
test-consistency:
	echo 'testing repo consistency ...' &&\
	python tests/test_repo_consistency.py

.PHONY: test-mypy
test-mypy:
	echo 'running mypy ...' &&\
	mypy .

.PHONY: test-pylint
test-pylint:
	echo 'running pylint ...' &&\
	pylint app_lib &&\
	pylint tests

.PHONY: test-pytest-local
test-pytest-local:
	echo 'running pytest (local tests only) ...' &&\
	pytest \
	--cov=app_lib \
	--cov-fail-under ${PYTEST_FAIL_UNDER_COVERAGE} \
	-m "not external_deps"

.PHONY: test-pytest
test-pytest:
	echo 'running pytest ...' &&\
	pytest \
	--cov=app_lib \
	--cov-fail-under ${PYTEST_FAIL_UNDER_COVERAGE}

# run all tests that do not require internet
.PHONY: test-local
test-local: test-consistency test-mypy test-pylint test-pytest-local

# run all tests
.PHONY: test
test: test-consistency test-mypy test-pylint test-pytest

#####################
# Flask Development #
#####################

# references env variables defined in Dockerfile
.PHONY: flask-server-dev
flask-server-dev:
	export FLASK_APP=${FLASK_APP_MODULE_LOCATION} &&\
	export FLASK_ENV=development &&\
	flask run --host=0.0.0.0

# references env variables defined in Dockerfile
.PHONY: flask-server
flask-server:
	export FLASK_APP=${FLASK_APP_MODULE_LOCATION} &&\
	flask run --host=0.0.0.0

# references env variables defined in Dockerfile
.PHONY: gunicorn-server
gunicorn-server:
	gunicorn \
	--bind ":${PORT}" \
	--workers ${FLASK_APP_WORKERS} \
	--threads ${FLASK_APP_THREADS} \
	--timeout ${FLASK_APP_TIMEOUT} \
	"${FLASK_APP_MODULE_LOCATION}:${FLASK_APP_NAME_IN_CODE}"

##############
# Deployment #
##############

.PHONY: build-prod
build-prod:
	bash scripts.sh --build-prod

.PHONY: gcloud-auth
gcloud-auth:
	gcloud auth activate-service-account ${GCLOUD_SERVICE_ACCOUNT} --key-file="google_key.json"

.PHONY: gcloud-deploy
gcloud-deploy:
	docker tag ${PROD_IMAGE_NAME} gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME} &&\
    docker push gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME} &&\
	gcloud run deploy ${GCLOUD_SERVICE_NAME} ${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} --image=gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME}

#######
# Ray #
#######

.PHONY: ray-start
ray-start:
	ray start \
      --head \
      --port=6379 \
      --object-manager-port=8076 \
      --include-dashboard=true \
      --dashboard-host=0.0.0.0 \
      --dashboard-port=8265

.PHONY: ray-stop
ray-stop:
	ray stop
