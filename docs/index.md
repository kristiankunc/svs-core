# SVS

- *🇬🇧 self-hosted virtual stack*
- *🇨🇿 studentský vývojový server*

---

- [Installation Quickstart guide](setup/quickstart.md)
- [CLI documentation](cli.md)
- [API documentation](api/index.md)
- [Changelog](#changelog)
- [Paper](#paper)

## Introduction

SVS is a python library designed to provide users with an easy way to deploy containerized services on a host machine. It abstracts away the complexities of container orchestration, allowing users to focus on deploying and managing their applications with minimal effort.

## Support

Support is offered through the QnA section on [GitHub Discussions](https://github.com/kristiankunc/svs-core/discussions/categories/q-a).

---

## Looking to deploy a service?

Head over to the [Guide for users](guides/index.md) to learn how to deploy your first service with SVS.

## How does it work?

In this chapter, you can read about the core concepts and philosophy behind SVS.

SVS is designed for home labs and small-scale deployments. It leverages Docker to manage containerized applications, providing a simple interface for users to deploy, monitor, and manage their services.

If you are unfamiliar with Docker, it is recommended to read the [Docker documentation](https://docs.docker.com/get-started/overview/) first so you understand the underlying technology SVS is built upon.

Key concepts you should be familiar with when using SVS:

- Docker images
- Docker containers
- Docker networks
- Docker volumes (specifically bind mounts)

This guide will refer to these concepts frequently so a basic understanding is essential.

### User

Multiple users are supported, each user has its own isolated environment for deploying services. Users can manage their services independently without interfering with each other.

Each user has:

- A corresponding system user on the host machine.
- A private Docker network all their services are attached to.

There are two types of users in SVS:
1) **Admin users**: These users have elevated privileges and can manage other users, templates, and system-wide settings.
2) **Regular users**: These users can only manage their own services and settings.

### Template

A template is a predefined configuration for a specific service. It includes details such as the Docker image to use, environment variables, volume mounts, and network settings. Users can deploy services based on these templates, simplifying the deployment process.

Think of it like an extended variant of a [Docker compose file](https://docs.docker.com/compose/intro/features-uses/). As opposed to Docker compose, SVS templates are stored in JSON and include additional metadata used by SVS.

There are two types of templates:

- **IMAGE** templates: These templates specify a Docker image to be used for the service. These images are pre-built and can be pulled from a Docker registry directly. A good example of such template is the [NGINX template](https://github.com/kristiankunc/svs-core/blob/main/service_templates/nginx.json)
- **BUILD** templates: These templates include instructions to build a Docker image from a Dockerfile. When a service is deployed using a BUILD template, SVS will first build the Docker image according to the specified instructions before running the service. A good example of such template is the [Django template](https://github.com/kristiankunc/svs-core/blob/main/service_templates/django.json)

### Service
A service is an instance of a deployed application based on a template. Each service runs in its own Docker container, isolated from other services and users.

???+ note "User mode containers"
    To ensure safe permission mapping to the host system, all services are run in "user mode". This means that the Docker containers run with the same user ID (UID) as the system user they belong to. This prevents permission issues when services need to read or write files on the host system.

    Note that not all Docker images are compatible with user mode. Always check the image documentation to ensure compatibility.

### Backend

This chapter gets into more technical details about how SVS works under the hood.

#### User groups

All admin users are part of the `svs-admins` system group. This allows admin users to manage files and directories created by other users.

#### System Containers

SVS relies on two system containers to function properly:

1. **PSQL Database**: This container runs a PostgreSQL database that stores all metadata related to users, templates, and services.
2. **Reverse Proxy**: This container runs a Caddy server that acts as a reverse proxy for all deployed services, handling incoming requests and routing them to the appropriate service containers.

Configuration for these containers is stored in  `/etc/svs/docker/` directory on the host machine. It includes a Docker Compose files and an environment variable file required to run the containers.

!!! warning
    Once the database container is initialized, changing the credentials in the environment file will not have any effect as the database does not automatically update existing credentials. To change the database credentials, you will need to manually update them in the database itself.

#### Logging

A log file is maintained at `/etc/svs/svs.log` on the host machine. This log file contains important information about the operations performed by SVS, including errors and warnings.

#### Data storage

All container data (bind mounts) are stored in `/var/svs/volumes` directory on the host machine. Each user has their own subdirectory (keyed by their ID) where all their service data is stored. The subdirectories are automatically generated for each service. A service can have multiple bind mounts, each stored in its own subdirectory.

## Paper

[View raw](main.pdf){target="_blank"}

![PDF paper](main.pdf){ type=application/pdf style="min-height:100vh;width:100%"}

## Changelog

--8<-- "CHANGELOG.md:2"
