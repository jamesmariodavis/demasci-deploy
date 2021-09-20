# syntax=docker/dockerfile:1.3

##############
# Base Image #
##############
FROM python:3.9-slim-bullseye as base-image

# build path is used to install dependencies in image
ENV BUILD_PATH=/build
WORKDIR ${BUILD_PATH}

# install dependencies of build
RUN apt-get update \
    && apt-get -y install \
    --no-install-recommends \
    --no-install-suggests \
    bash \
    curl \
    liblapack-dev \
    make \
    redis-server \
    && apt-get clean \
    && rm -rf /var/cache/apt/lists

# poetry stuff
ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.1.6 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

ENV PATH="${PATH}:/root/.local/bin:${POETRY_HOME}/bin"

# copy files for poetry install
COPY pyproject.toml ${BUILD_PATH}/pyproject.toml
COPY poetry.lock ${BUILD_PATH}/poetry.lock

# install poetry, python, and libraries - respects $POETRY_VERSION & $POETRY_HOME
# must install ray with extras via pip
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python - \
    && pip install --upgrade pip \
    && poetry install --no-dev \
    && yes | poetry cache clear --all . \
    && rm -rf /root/.cache/*

##############
# Prod Image #
##############
FROM python:3.9-slim-bullseye as prod-image

# where code will be mounted in docker container
ARG DOCKER_CODE_MOUNT_DIRECTORY_ARG

# copy python and libraries
COPY --from=base-image /usr/local/bin /usr/local/bin
COPY --from=base-image /usr/local/lib/python3.9 /usr/local/lib/python3.9

# install minimal dependencies for prod
# liblapack-dev referenced by scientific computing (numpy)
RUN apt-get update \
    && apt-get -y install \
    --no-install-recommends \
    --no-install-suggests \
    bash \
    curl \
    liblapack-dev \
    make \
    redis-server \
    && apt-get clean \
    && rm -rf /var/cache/apt/lists

# allow statements and log messages to immediately appear in the Knative logs in server
ENV PYTHONUNBUFFERED=True

# copy code and set work directory
# note that code is copied to image in prod
# changes to code after build will not affect copied code
WORKDIR ${DOCKER_CODE_MOUNT_DIRECTORY_ARG}
ENV PYTHONPATH=${DOCKER_CODE_MOUNT_DIRECTORY_ARG}
COPY . /${DOCKER_CODE_MOUNT_DIRECTORY_ARG}/

# set command when invoking docker run
CMD ["bash", "docker/prod.sh"]

#############
# Dev Image #
#############
FROM base-image as dev-image

# used to configure gcloud in dev image
ARG GCLOUD_REGION_ARG
# used to set PORT env variable
ARG API_TEST_PORT_ARG
# where code will be mounted in docker container
ARG DOCKER_CODE_MOUNT_DIRECTORY_ARG
# location of service account key file
ARG GCLOUD_SERVICE_ACCOUNT_KEY_FILE_ARG

# install additional dependencies
RUN apt-get update \
    && apt-get -y install \
    git \
    jq \
    && apt-get clean \
    && rm -rf /var/cache/apt/lists

# install docker
# see "socket solution": https://jpetazzo.github.io/2015/09/03/do-not-use-docker-in-docker-for-ci/
RUN apt-get update \
    && apt-get -y install \
    --no-install-recommends \
    --no-install-suggests \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    # lsb-release installs python3 in /usr/bin
    lsb-release \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo \
    "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
    $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get -y install \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    && apt-get clean \
    && rm -rf /var/cache/apt/lists \
    && yes | poetry cache clear --all . \
    && rm -rf /root/.cache/*

# install gcloud
RUN	curl -sSL https://sdk.cloud.google.com > gcl \
    && bash gcl \
    --install-dir=/gcloud \
    --disable-prompts
ENV PATH="${PATH}:/gcloud/google-cloud-sdk/bin"
RUN gcloud config set run/region ${GCLOUD_REGION_ARG} &&\
    gcloud auth configure-docker

# set credentials path for gcloud
# https://cloud.google.com/docs/authentication/production#auth-cloud-implicit-python
ENV GOOGLE_APPLICATION_CREDENTIALS=${DOCKER_CODE_MOUNT_DIRECTORY_ARG}/${GCLOUD_SERVICE_ACCOUNT_KEY_FILE_ARG}

# PORT is part of the container contract in Cloud Run
# https://cloud.google.com/run/docs/reference/container-contract
# simulate PORT contract with static reference in dev
ENV PORT=${API_TEST_PORT}

# install k8s
RUN command apt-get update \
    && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    && curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list \
    && apt-get update \
    && apt-get install -y kubectl \
    && apt-get clean \
    && rm -rf /var/cache/apt/lists

# install all python libraries, including dev
RUN poetry install

# clean up build
WORKDIR /
RUN rm -rf ${BUILD_PATH}
