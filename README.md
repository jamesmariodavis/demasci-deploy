# Overview and Preliminaries
This repository is designed to be a skeleton for a DS centric python project. It is functional across platforms (Mac, Windows, Linux). It uses various technologies to:
- manage Docker images/containers for development and production
- create a containerized webserver on Google Cloud Run
- interface with Google Sheets (used as a UI for an application)

To use this skeleton effectively you must have the following installed locally:
- [Docker Desktop](https://www.docker.com/get-started)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (use `git --version` to check if pre-installed)

It is expected that [VSCode](#vscode) is used for development.

Throughout the README we reference variables to be replaced by the user with `<variable>`.

## Gotchas
The repo name is used to tag Docker images. The name of the upstream fetch source in Docker must match the top level directory name locally. This impacts coordinating Docker image names in `scripts.sh` and `.devcontainer/devcontainer.json`.

The flask application file and name (distinct from the application name) is a required reference when starting the webserver. The current file name is `flask_app.py`. This is referenced in `docker/Dockerfile.base` as an environment variable and requires manual coordination.

There is a reference to a flask app in the flash application file (`flask_app.py`). Currently it is `app`. This is referenced in `docker/Dockerfile.base` as an environment variable and requires manual configuration.

## Note on Windows
This is a Linux/Mac centric codebase. However, this can easily be used in Windows. Windows usage requires (in addition to the requirements below) WSL 2.0 and associated Linux distro.
- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [latest Ubuntu LTS Release for WSL](https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71) Search Windows Marketplace for updated version.

Windows users should use Powershell as their main entry point for commands. To use `gcloud` on Windows you must install a small package that interfaces with Google Cloud SDK. See here: https://cloud.google.com/tools/powershell/docs/quickstart

To use Git commands on Windows you can either install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (not recommended) or depend on the pre-installed version of Git in WSL. To leverage WSL prefix `wsl` to Git commands. For example, to clone this repository open Powershell and execute:
```
wsl git clone
```
Similarly for other commands prefixing `wsl` may be required.

**Do not edit any files in Windows**. Instead, [open VSCode in a container](#vscode) and edit files there. Editing files in Windows will change the carriage return charachter and [break the codebase](https://en.wikipedia.org/wiki/Newline#Issues_with_different_newline_formats).


## `scripts.sh`

The repository provides a set of scripts for Bash in `scripts.sh`. These are intended to be run on the local machine, never in a Docker container. These scripts:
- execute Docker build commands
- execute Docker run commands
- clean up local system

Run `scripts.sh` with the `--help` argument for more information. To invoke scripts:
```
bash scripts.sh <argument>
```

## VSCode
Development is expected to be done using VSCode [within a container](https://code.visualstudio.com/docs/remote/containers). The folder `.devcontainer` contains the configuration for using VScode in a container, including all required extensions. This should work out of the box.

VScode must be installed on the local machine with some dependencies:
- [VSCode](https://code.visualstudio.com/download)
- [Remote - Containers (VSCode Extension)](https://code.visualstudio.com/docs/remote/containers)

# Setup GCP
- Install [Google Cloud SDK](https://cloud.google.com/sdk/docs/install). See [Note on Windows](#note-on-windows).
- [Enable billing](https://cloud.google.com/billing/docs/how-to/modify-project)
- [Enable API](https://support.google.com/googleapi/answer/6158841?hl=en)
- [Enable services](https://cloud.google.com/container-registry/docs/enable-service). Use the GCP UI.
- [Setup authentication](https://cloud.google.com/container-registry/docs/advanced-authentication). Note: unless otherwise configured your "Windows Domain" is likely `WORKGROUP` and can be left blank.

```
gcloud init
gcloud auth login
gcloud auth configure-docker
gcloud config set run/region us-west1
gcloud services enable containerregistry.googleapis.com
gcloud run deploy --image=gcr.io/python-base-325100/python_base-prod:latest
```