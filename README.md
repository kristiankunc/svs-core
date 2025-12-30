# Self-Hosted Virtual Stack

**SVS is an open-source python library for managing self-hosted services on a linux server.**

[![PyPI version](https://img.shields.io/pypi/v/svs-core.svg)](https://pypi.org/project/svs-core/)
[![codecov](https://codecov.io/gh/kristiankunc/svs-core/branch/main/graph/badge.svg)](https://codecov.io/gh/kristiankunc/svs-core)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://pre-commit.com/)
[![Release Please](https://img.shields.io/badge/release--please-automated-blue)](https://github.com/googleapis/release-please)

CI:

[![Publish Python Package](https://github.com/kristiankunc/svs-core/actions/workflows/publish.yml/badge.svg?event=release)](https://github.com/kristiankunc/svs-core/actions/workflows/publish.yml)
[![Test](https://github.com/kristiankunc/svs-core/actions/workflows/test.yml/badge.svg)](https://github.com/kristiankunc/svs-core/actions/workflows/test.yml)

## Docs

**For full docs, visit [svs.kristn.co.uk](https://svs.kristn.co.uk/)**

This readme contains a quick summary and development setup info.


## Goals

The goal of this project is to provide a simple and easy-to-use library for managing self-hosted services on a linux server. It is designed to be used by developers who want to automate the management of their self-hosted services, such as web servers, databases, and other applications.

It should be both begginer-friendly and yet allow advanced users to customize the behavior of the library to suit their needs.

Under the hood, all services will be managed using Docker containers, which allows for easy deployment and management of services. Given the complexity of Docker, the library will provide templates for common services and hide as much of the complexity as possible while still allowing advanced users to access the underlying Docker functionality if they wish to do so.

## Technology overview

Every service will run a Docker container and all of users' services will be on the same Docker network, allowing them to communicate with each other easily without

1. exposing them to other users on the same server
1. having to use compose stacks and custom networks to allow cross-service communication.

## Features

Currently, the library is in early development and has the following features:

- [x] User management
- [x] Docker network management
- [x] Service management
- [x] Service templates
- [ ] CI/CD integration
- [ ] DB/System sync issues + recovery
- [x] Remote SSH access

## Running locally

Given this repository accesses system files, creates docker containers and manages services and is designed strictly for linux servers, it is recommended to run in a virtual environment.

The easiest way to achieve a reproducible environment is to use the included devcontainer configuration. Devcontainers allow you to run a containerized development environment with all dependencies installed. [See the devcontainer documentation](https://code.visualstudio.com/docs/devcontainers/containers).

The local devcontainer config creates the following compose stack:

1. A `python` devcontainer for the development environment.
1. A `postgres` database container for storing service data.
1. A `caddy` container to act as a HTTP proxy (needed only if testing domains locally)

This guide assumes you have chosen to use the devcontainer setup.

### Starting the devcontainer

To start the devcontainer, open the repository in Visual Studio Code and select "Reopen in Container" from the command palette. This will build the container and start it.

After attaching to the devcontainer, the dependencies will be automatically installed. After that's done, you can launch a new terminal which will have the virtual environment activated automatically.

### Linting + Formatting

The devcontainer includes pre-configured linting and formatting tools for Visual Studio Code and all files should be formatted on save. If you use a different editor, you can run the pre-commit hooks manually by running `pre-commit run --all-files` in the terminal to apply the formatting and linting rules.

### Running the tests

To run the tests, you can use the `pytest` command in the terminal. This will run all tests in the `tests` directory. You can also run individual test files or functions by specifying their paths.

Tests are split into unit, integration and cli tests. They can be run separately by using the `-m` flag with pytest:

```bash
pytest -m unit
pytest -m integration
pytest -m cli
```

### Running the docs

Python docstrings are used throughout the codebase to generate documentation. To generate the documentation, you can use the `zensical` command in the terminal. This will build the documentation and serve it locally.
To run the documentation server, you can use the following command:

```bash
zensical serve
```
