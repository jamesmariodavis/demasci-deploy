# Overview and Preliminaries
This repository is designed to be a skeleton for a DS centric python project. It is functional across platforms (Mac, Windows, Linux). It uses various technologies to:
- manage Docker images/containers for development and production
- create a containerized webserver on Google Cloud Run
- interface with Google Sheets (used as a UI for an application)

To use this skeleton effectively you must have the following installed locally:
- [Docker Desktop](https://www.docker.com/get-started)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (use `git --version` to check if pre-installed)

It is expected that [VSCode](#vscode) is used for development.

## Gotchas
The application name is used to tag Docker images. See [relevant section](#set-application-name) on how to coordinate these files with a script. These tags are coordinated across:
- `scripts.sh`
- `.devcontainer/devcontainer.json`
- `pyproject.toml`

The flask application file and name (distinct from the application name) is a required reference when starting the webserver. The current file name is `flask_app.py`. This is referenced in `docker/Dockerfile.base` as an environment variable and requires manual coordination.

There is a reference to a flask app in the flash application file (`flask_app.py`). Currently it is `app`. This is referenced in `docker/Dockerfile.base` as an environment variable and required manual configuration.

## Note on Windows (Critical!)
This is a Linux/Mac centric codebase. However, this can easily be used in Windows. Windows usage requires (in addition to the requirements below) WSL 2.0 and associated Linux distro.
- [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
- [latest Ubuntu LTS Release for WSL](https://www.microsoft.com/en-us/p/ubuntu-2004-lts/9n6svws3rx71) Search Windows Marketplace for updated version.

Windows users should use Powershell as their main entry point for commands.

To use Git commands on Windows you can either install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) (not recommended) or depend on the pre-installed version of Git in WSL. To leverage WSL prefix `wsl` to Git commands. For example, to clone this repository open Powershell and execute:
```
wsl git clone
```
Similarly for other commands prefixing `wsl` may be required.

**Do not edit any files in Windows**. Instead, [open VSCode in a container](#vscode) and edit files there. Editing files in Windows will change the carriage return charachter and [break the codebase](https://en.wikipedia.org/wiki/Newline#Issues_with_different_newline_formats).


## `scripts.sh`

The repository provides a set of scripts for Bash in `scripts.sh`. These are intended to be run on the local machine, never in a Docker container. These scripts:
- initialize the repository for a new application
- execute Docker build commands
- execute Docker run commands
- clean up local system

Run `scripts.sh` with the `--help` argument for more information. To invoke scripts:
```
bash scripts.sh <argument>
```
Throughout the readme we reference variables to be replaced by the user with `<variable>`.

## Set Application Name
The skeleton is based around an application (app) name. The current app name is `python_base`. The app should be changed prior to any other operations as it cascades to Docker image names. Do not name your app `app` or `flask_app`.

To programatically change the app name and get feedback about the changes run:
```
bash scripts.sh --set-app-name <app_name>
```

The base file structure should, in most cases, be related to the app name as well. These changes must be made manually. The directory structure is below:
```
<repository_name>
+-- <python_code_folder>
+-- README.md
+-- scripts.sh
+-- ...
```
In most circumstances `<repository_name>` and `<python_code_folder>` should be the same as `<app_name>`. In the current repository each of these is set to `python_base`.

## VSCode
Development is expected to be done using VSCode [within a container](https://code.visualstudio.com/docs/remote/containers). The folder `.devcontainer` contains the configuration for using VScode in a container, including all required extensions. This should work out of the box.

VScode must be installed on the local machine with some dependencies:
- [VSCode](https://code.visualstudio.com/download)
- [Remote - Containers (VSCode Extension)](https://code.visualstudio.com/docs/remote/containers)