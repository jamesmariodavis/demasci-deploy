# Docker
This repo depends on multistage Docker builds, each with a required set of build args.
Each stage is define in the same Dockerfile.
It is safe to pass all build args to all stages.
You can find the buid args in  `scripts.sh`.

There are 3 stages.
The stages are:
- `base-image`: Sets environment variables required in production. Installs poetry and python libraries.
- `prod-image`: Intended for remote deployment. All code is copied to `DOCKER_CODE_MOUNT_DIRECTORY_ARG`. Contains all required packages, binaries, and environment variables. Satisfies [Google Cloud Run contract](https://cloud.google.com/run/docs/reference/container-contract).
- `dev-image`: Intended for local development. Specifically designed to work with VSCode. Contains additional development tools (docker, gcloud). Contains requirements to build additional binaries. Significantly larger in size than `prod`.

The images form a tree with leaf nodes `prod` and `dev`. The images must be built in order:
```
|-- base-image
    |-- prod-image
    |-- dev-image
```

To build all stages and create two named images run:
```
bash scripts.sh --build
```