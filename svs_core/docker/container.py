from typing import Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client
from svs_core.docker.json_properties import Label


class DockerContainerManager:
    @classmethod
    def create_container(
        cls,
        name: str,
        image: str,
        command: Optional[str] = None,
        args: Optional[list[str]] = None,
        labels: list[Label] = [],
    ) -> Container:
        """
        Create a Docker container.

        Args:
            name (str): The name of the container.
            image (str): The Docker image to use.
            command (Optional[str]): The command to run in the container.
            args (Optional[List[str]]): The arguments for the command.
                These will be combined with command to form the full command.
            labels (List[Label]): Docker labels to apply to the container.

        Returns:
            Container: The created Docker container instance.
        """
        client = get_docker_client()

        # Combine command and args if both are provided
        full_command = None
        if command and args:
            # Create a string with command and all args
            full_command = f"{command} {' '.join(args)}"
        elif command:
            full_command = command
        elif args:
            # If only args are provided, join them as a command
            full_command = " ".join(args)

        return client.containers.create(
            image=image,
            name=name,
            command=full_command,
            detach=True,
            labels={label.key: label.value for label in labels},
        )

    @classmethod
    def get_container(cls, container_id: str) -> Optional[Container]:
        """
        Retrieve a Docker container by its ID.

        Args:
            container_id (str): The ID of the container to retrieve.

        Returns:
            Optional[Container]: The Docker container instance if found, otherwise None.
        """
        client = get_docker_client()
        try:
            container = client.containers.get(container_id)
            return container
        except Exception:
            return None

    @classmethod
    def start_container(cls, container: Container) -> None:
        """
        Start a Docker container.

        Args:
            container (Container): The Docker container instance to start.
        """
        container.start()
