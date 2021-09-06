# Docker
This repo depends on multistage Docker builds, each with a required set of build args.
It is safe to pass all build args to all stages.
The following build args are used (copied from `scripts.sh`):
```
    --build-arg FLASK_APP_MODULE_LOCATION_ARG=${FLASK_APP_MODULE_LOCATION} \
    --build-arg FLASK_APP_NAME_IN_CODE_ARG=${FLASK_APP_NAME_IN_CODE} \
    --build-arg FLASK_APP_PORT_ARG=${FLASK_APP_PORT} \
    --build-arg FLASK_APP_WORKERS_ARG=${FLASK_APP_WORKERS} \
    --build-arg FLASK_APP_THREADS_ARG=${FLASK_APP_THREADS} \
    --build-arg FLASK_APP_TIMEOUT_ARG=${FLASK_APP_TIMEOUT} \
    --build-arg DOCKER_CODE_MOUNT_DIRECTORY_ARG=${DOCKER_CODE_MOUNT_DIRECTORY} \
    --build-arg INCLUDE_CBC=${INCLUDE_CBC} \
    --build-arg GCLOUD_PROJECT_ID_ARG=${GCLOUD_PROJECT_ID} \
    --build-arg GCLOUD_REGION_ARG=${GCLOUD_REGION} \
    --build-arg GCLOUD_SERVICE_NAME_ARG=${GCLOUD_SERVICE_NAME} \
    --build-arg GCLOUD_ALLOW_UNAUTHENTICATED_PARAM_ARG=${GCLOUD_ALLOW_UNAUTHENTICATED_PARAM} \
    --build-arg GCLOUD_SERVICE_ACCOUNT_ARG=${GCLOUD_SERVICE_ACCOUNT} \
    --build-arg GCLOUD_APP_URL_ARG=${GCLOUD_APP_URL} \
    --build-arg PROD_IMAGE_NAME_ARG=${PROD_IMAGE_NAME} \
    --build-arg BASE_IMAGE_NAME_ARG=${BASE_IMAGE_NAME} \
    --build-arg BASE_BUILDER_IMAGE_NAME_ARG=${BASE_BUILDER_IMAGE_NAME} \
```

There are 4 names images:
- `base-builder`: Contains tools to build all code from source. Code with significant compile times (CBC, numpy, pandas) are built here. Takes significant time (~20 min) ti build. Build infrequently.
- `base`: Copies binaries from `base-builder`. Builds or updates additional, faster building, components. Sets environment variables required in production.
- `prod`: Intended for remote deployment. All code is copied to `DOCKER_CODE_MOUNT_DIRECTORY_ARG`. Contains all required packages, binaries, and environment variables. Satisfies [Google Cloud Run contract](https://cloud.google.com/run/docs/reference/container-contract).
- `dev`: Intended for local development. Specifically designed to work with VSCode. Contains additional development tools (docker, gcloud). Contains requirements to build additional binaries. Significantly larger in size than `prod`.

The images form a tree with leaf nodes `prod` and `dev`. The images must be built in order:
```
|-- base-builder
    |-- base
        |-- prod
        |-- dev
```