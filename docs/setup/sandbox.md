# Testing sandbox

The SVS sandbox provides a pre-configured [Docker in Docker (DIND)](https://www.docker.com/resources/docker-in-docker-containerized-ci-workflows-dockercon-2023/#what-is-docker-in-docker) environment for quick testing and evaluation - no bare-metal installation required.

It runs a Docker container that has Docker installed within it, allowing you to use SVS inside this isolated environment without affecting your host system.

!!! warning "Not for production use"
    The SVS Sandbox is intended for quick testing and evaluation purposes only. It is not recommended for production environments.

## Prerequisites

- Docker daemon installed and running - [Docker installation guide](https://docs.docker.com/engine/install/)

## Quick start

The sandbox auto-initializes on first boot - just start it and jump in:

```bash
# Start the container (auto-initializes SVS)
docker run -d --privileged --name svs-sandbox ghcr.io/kristiankunc/svs-core-sandbox:latest

# Access the shell - SVS is ready to use
docker exec -it svs-sandbox bash
```

The container automatically:
1. Starts the Docker daemon
2. Runs `svs init --yes` to set up the PostgreSQL + Caddy stack, run migrations, import templates, and create a default admin user

Default admin credentials: **`admin` / `admin`**

### Verify

```bash
svs user list
```

You're all set! Start creating services or exploring the CLI.

## Building locally

If you want to build the sandbox from source instead of using the pre-built image:

```bash
# Using the production Dockerfile
cd sandbox-env
docker compose build

# Or using the local development Dockerfile (uses your local code checkout)
docker compose -f docker-compose.yml -f docker-compose.local.yml build
```

## Data persistence

**Keep in mind that unless you set up persistent storage, all data will be lost once the container is removed.** The sandbox is for evaluation, not long-term use.

## Clean up

To remove the sandbox container and all its data:

```bash
docker rm -f svs-sandbox
```
