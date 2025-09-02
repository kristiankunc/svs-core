from typing import Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client


class DockerContainerManager:
    @classmethod
    def create_container(
        cls,
        name: str,
        image: str,
        command: Optional[str] = None,
        args: Optional[list[str]] = None,
    ) -> Container:
        """
        Create a Docker container.

        Args:
            name (str): The name of the container.
            image (str): The Docker image to use.
            command (Optional[str]): The command to run in the container.
            args (Optional[List[str]]): The arguments for the command.

        Returns:
            Container: The created Docker container instance.
        """
        client = get_docker_client()

        return client.containers.create(
            image=image,
            name=name,
            command=command,
            args=args or [],
            detach=True,
        )
