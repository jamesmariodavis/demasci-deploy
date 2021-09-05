# Quick Start
All commands in `scripts.sh` are intended to be run on local machine.
All commands in `Makefile` are intended to be run in development container.
Set configuration in `configure.sh`. URLs may not be known until after first deploy.

Build all containers on local system:
```
bash scripts.sh --build
```
Enter dev container:
```
bash scripts.sh --enter-dev
```
Authorize with `gcloud` inside dev container (this will prompt with further instructions):
```
make gcloud-auth
```
Deploy code to Cloud Run
```
make delpoy
```

To test deployment works URLs must be appropriately configured in `configure.sh`.
After configuration is correct rebuild all images (`bash scripts.sh --build`).
To verify URL is functional enter container and run:
```
make gcloud-curl
```

# Overview and Preliminaries
This repository is designed to be a skeleton for a DS centric python project. It is functional across platforms (Mac, Windows, Linux). It uses various technologies to:
- manage Docker images/containers for development and production
- create a containerized webserver on Google Cloud Run
- interface with Google Sheets (used as a UI for an application)

To use this skeleton effectively you must have the following installed locally:
- [Docker Desktop](https://www.docker.com/get-started)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (use `git --version` to check if pre-installed)

It is expected that [VSCode](#vscode) is used for development.

Throughout the README we reference variables to be replaced by the user with `<variable>`.

## Gotchas
The repo name is used to tag Docker images.
The name of the upstream fetch source in Docker must match the top level directory name locally.
This impacts coordinating Docker image names in `scripts.sh` and `.devcontainer/devcontainer.json`.

The flask application file and name (distinct from the application name) is a required reference when starting the webserver.
The current file name is `flask_app.py`.
This is referenced in `configure.sh` as an environment variable and requires manual coordination.

There is a reference to a flask app name in the flask application file (`flask_app.py`).
Currently it is `app`.
This is referenced in `configure.sh` as an environment variable and requires manual configuration.

## Note on Windows
This is a Linux/Mac centric codebase. However, this can easily be used in Windows. Windows usage requires (in addition to the requirements below) WSL 2.0 and associated Linux distro.
- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [latest Ubuntu LTS Release for WSL](https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71) Search Windows Marketplace for updated version.

Windows users should use Powershell as their main entry point for commands.

To use Git commands on Windows you can either install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (not recommended) or depend on the pre-installed version of Git in WSL.
To leverage WSL prefix `wsl` to Git commands. For example, to clone this repository open Powershell and execute:
```
wsl git clone
```
Similarly for other commands prefixing `wsl` may be required.

**Do not edit any files in Windows**.
Instead, [open VSCode in a container](#vscode) and edit files there.
Editing files in Windows will change the carriage return charachter and [break the codebase](https://en.wikipedia.org/wiki/Newline#Issues_with_different_newline_formats).


## `scripts.sh`

The repository provides a set of scripts for Bash in `scripts.sh`. These are intended to be run on the local machine, never in a Docker container. These scripts:
- execute Docker build commands
- execute Docker run commands
- clean Docker system

Run `scripts.sh` with the `--help` argument for more information. To invoke scripts:
```
bash scripts.sh <argument>
```

## `configure.sh`

Configuration of the repository is primarily captured in `configure.sh`.
Read and modify values there as appropriate for your use case.
There are additional configuration components in `pyproject.toml`.

## VSCode
Development is expected to be done using VSCode [within a container](https://code.visualstudio.com/docs/remote/containers).
The folder `.devcontainer` contains the configuration for using VScode in a container, including all required extensions.
This should work without modification.

VScode must be installed on the local machine with some dependencies:
- [VSCode](https://code.visualstudio.com/download)
- [Remote - Containers (VSCode Extension)](https://code.visualstudio.com/docs/remote/containers)

# Setup GCP
To use Google Cloud we interact the web UI, Google Cloud Console, rather than depend on scripting. You will need to:
- [Create a Google Cloud account](https://cloud.google.com/)
- [Create a project](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
- [Enable billing](https://cloud.google.com/billing/docs/how-to/modify-project). Navigate to Billing in Google Cloud Console.
- [Enable Google Run API](https://support.google.com/googleapi/answer/6158841?hl=en). This is non-essential: the first deployment will prompt for enabling required APIs.
- [Enable Container Registry service](https://cloud.google.com/container-registry/docs/enable-service). Navigate to Container Registry in Google Cloud Console.

There are many avaiable services. This repo depends on a small number of them. It is useful to pin these services in Google Cloud Console:
- Cloud RUN
- Container Registry
- IAM & Admin

Once complete add key information, especially project ID, to `configure.sh`.

For common issues with Cloud Run see [here](https://cloud.google.com/run/docs/troubleshooting). It will be especially important to manage permissions related to the Cloud Run Invoker role when calling the service in Cloud Run.
