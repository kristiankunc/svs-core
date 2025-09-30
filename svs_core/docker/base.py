import docker


def get_docker_client() -> docker.DockerClient:
    """Returns a Docker client instance.

    Returns:
        docker.DockerClient: A Docker client instance.
    """
    return docker.from_env()
