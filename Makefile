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

.PHONY: gcloud-push-image
gcloud-push-image: test build-prod
	docker tag ${PROD_IMAGE_NAME} ${GCLOUD_PROD_IMAGE_NAME} \
    && docker push ${GCLOUD_PROD_IMAGE_NAME}

.PHONY: gcloud-run-deploy
gcloud-run-deploy: gcloud-push-image
	gcloud run deploy ${GCLOUD_SERVICE_NAME} ${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} --image=${GCLOUD_PROD_IMAGE_NAME}

.PHONY: gcloud-k8s-create
gcloud-k8s-create:
	gcloud config set compute/zone ${GCLOUD_ZONE} \
	&& gcloud config set compute/region ${GCLOUD_REGION} \
	&& gcloud container clusters create ${GCLOUD_K8S_CLUSTER_NAME} --num-nodes=1

.PHONY: gcloud-k8s-context
gcloud-k8s-context:
	gcloud container clusters get-credentials ${GCLOUD_K8S_CLUSTER_NAME} \
	&& kubectl config use-context ${GCLOUD_K8S_CONTEXT_NAME}

.PHONY: gcloud-k8s-deploy
gcloud-k8s-deploy: gcloud-push-image gcloud-k8s-context k8s-deploy

.PHONY: gcloud-k8s-delete
gcloud-k8s-delete: gcloud-k8s-context
	gcloud container clusters delete ${GCLOUD_K8S_CLUSTER_NAME}


##############
# Kubernetes #
##############

# note this will deploy to current kubectl context
.PHONY: k8s-deploy
k8s-deploy:
	kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v${K8S_DASHBOARD_VERSION}/aio/deploy/recommended.yaml \
	&& kubectl patch deployment kubernetes-dashboard -n kubernetes-dashboard --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--enable-skip-login"}]' \
	&& kubectl apply -f k8s/python-api.yml

.PHONY: k8s-local-context
k8s-local-context:
	kubectl config use-context ${K8S_LOCAL_CONTEXT_NAME}

.PHONY: k8s-local-deploy
k8s-local-deploy: gcloud-push-image k8s-local-context k8s-deploy

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
