FROM python:3.7.5-slim-buster

# define build path and set to working directory
# build path is used to install dependencies in image
ENV BUILD_PATH /build/
WORKDIR ${BUILD_PATH}
COPY pyproject.toml ${BUILD_PATH}/pyproject.toml
COPY poetry.lock ${BUILD_PATH}/poetry.lock

# update pip to speed up poetry
RUN pip install --upgrade pip

# install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    gcc \
    python3-psutil \
    libpq-dev \
    curl \
    make \
    unzip \
    git \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

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

ENV PATH="${PATH}:/root/.local/bin"

# Install Poetry and update path - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
ENV PATH="${PATH}:${POETRY_HOME}/bin"

# install python
RUN poetry install

# install aws-cli
RUN curl "https://s3.amazonaws.com/aws-cli/awscli-bundle.zip" -o "awscli-bundle.zip" \
    && unzip awscli-bundle.zip \
    && ./awscli-bundle/install -i /usr/local/aws -b /usr/local/bin/aws
# copy credentials for aws cli
COPY docker/.aws /root/.aws

# clean up build
WORKDIR /
RUN rm -rf ${BUILD_PATH}