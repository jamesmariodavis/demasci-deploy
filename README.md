# Overview
This repository is designed to be a base skeleton for a python project. It is functional across platforms (Mac, Windows, Linux).

To use this skeleton effectively you must have the following installed locally:
- [Docker Desktop](https://www.docker.com/get-started)
- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [VSCode](https://code.visualstudio.com/download)
- [Remote - Containers (VSCode Extension)](https://code.visualstudio.com/docs/remote/containers)
- [Python (VSCode Extension)](https://code.visualstudio.com/docs/python/python-tutorial)
- [Pylance (VSCode Extension)](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Docker (VSCode Extension)](https://code.visualstudio.com/docs/containers/overview)

The repository provides tools to build Docker images, attach VSCode to Docker containers, and interface with GCP. It expects the following development workflow:
- build developer image
- attach VSCode to development container
- develop!

The repository provides a set of scripts for Windows powershell (`scripts.ps1`) and bash (`scripts.sh`). These scripts initlaize the repository for a new application and execute various Docker commands. Run the scripts with the `--help` argument for more information.

Throughout the readme we reference variables to be replaced by the user with `<variable>`.

# Set <app_name>
The skeleton is based around an application (app) name. The current app name is `python_base`. You should change the app name prior to any other operations.

To programatically change the app name and get feedback about the changes made run:
```
bash scripts.sh set-app-name <app_name>
```

The base file structure should, in most cases, be related to the app name as well. These changes must be made manually. The directory structure is below:
```
<repository_name>
+-- .devcontainer
+-- docker
+-- <python_code_folder>
+-- tests
+-- .dockerignore
+-- .gitignore
+-- .style.yapf
+-- Makefile
+-- poetry.lock
+-- pyproject.toml
+-- README.md
+-- scripts.ps1
+-- scripts.sh
```
In most circumstances `<repository_name>`, `<python_code_folder>`, should be the same as `<app_name>`. In the current repository each of these is set to `python_base`.
