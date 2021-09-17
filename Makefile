#!make

# load configuration variables
include configure.sh

GCLOUD_IDENTITY_TOKEN=$(shell gcloud auth print-identity-token)

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

###################
# API Development #
###################

# references env variables defined in Dockerfile
.PHONY: run-test-server
run-test-server:
	bash docker/prod.sh

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
	docker tag ${PROD_IMAGE_NAME} gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME} \
    && docker push gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME} \
	&& gcloud run deploy ${GCLOUD_SERVICE_NAME} ${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} --image=gcr.io/${GCLOUD_PROJECT_ID}/${PROD_IMAGE_NAME}

##############
# Kubernetes #
##############

.PHONY: k8s-local-deploy
k8s-local-deploy:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v${K8S_DASHBOARD_VERSION}/aio/deploy/recommended.yaml \
	&& kubectl patch deployment kubernetes-dashboard -n kubernetes-dashboard --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--enable-skip-login"}]' \
	&& kubectl apply -f k8s/uvicorn.yml


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
