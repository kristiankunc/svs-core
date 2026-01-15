# Testing sandbox

Uninstalling SVS from bare metal can be a little time consuming as no uninstall script is provided _yet_. To facilitate quick testing and evaluation, a pre-configured sandbox environment is provided using [Docker in Docker (DIND)](https://www.docker.com/resources/docker-in-docker-containerized-ci-workflows-dockercon-2023/#what-is-docker-in-docker).

It essentially runs a Docker container that has Docker installed within it, allowing you to run SVS inside this isolated environment without affecting your host system.

!!! warning "Not for production use"
    The SVS Sandbox is intended for quick testing and evaluation purposes only. It is not recommended for production environments.

## Prerequisites

The only requirement is to have Docker daemon installed - [Docker installation guide](https://docs.docker.com/engine/install/).

## Running the sandbox

1) Start the container in detached mode:

```bash
docker run -d --privileged --name svs-sandbox ghcr.io/kristiankunc/svs-core-sandbox:latest
```

2) Access the container's shell:

```bash
docker exec -it svs-sandbox bash
```

_You can ignore the `❌ Docker service is not running.` warning as long as running `docker ps` does not return an error._


## Setup

After accessing the container shell, you still have to run the standard install script. For further details on the setup script, refer to the [quickstart guide](quickstart.md#run-setup-script).

```bash
sudo bash /root/install.sh
```


The official templates are provided in `/usr/local/share/service_templates/`. You can import them using the CLI:

```bash
sudo svs template import -r /usr/local/share/service_templates/
```

After that you're all set to go! You can start creating and running services as usual. **Keep in mind that unless you set up persistent storage, all data will be lost once the container is removed.**
