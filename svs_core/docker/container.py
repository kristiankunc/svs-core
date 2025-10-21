from typing import Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client
from svs_core.docker.json_properties import Label
from svs_core.shared.logger import get_logger


class DockerContainerManager:
    """Class for managing Docker containers."""

    @staticmethod
    def create_container(
        name: str,
        image: str,
        command: Optional[str] = None,
        args: Optional[list[str]] = None,
        labels: list[Label] = [],
        ports: Optional[dict[str, int]] = None,
    ) -> Container:
        """Create a Docker container.

        Args:
            name (str): The name of the container.
            image (str): The Docker image to use.
            command (Optional[str]): The command to run in the container.
            args (Optional[List[str]]): The arguments for the command.
                These will be combined with command to form the full command.
            labels (List[Label]): Docker labels to apply to the container.
            ports (Optional[Dict[str, int]]): Port mappings for the container in the format {"container_port/protocol": host_port}.

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

        get_logger(__name__).debug(
            f"Creating container with config: name={name}, image={image}, command={full_command}, labels={labels}, ports={ports}"
        )

        return client.containers.create(
            image=image,
            name=name,
            command=full_command,
            detach=True,
            labels={label.key: label.value for label in labels},
            ports=ports or {},
        )

    @staticmethod
    def get_container(container_id: str) -> Optional[Container]:
        """Retrieve a Docker container by its ID.

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

    @staticmethod
    def get_all() -> list[Container]:
        """Get a list of all Docker containers.

        Returns:
            list[Container]: List of Docker Container objects.
        """
        client = get_docker_client()
        return client.containers.list(all=True)  # type: ignore

    @staticmethod
    def remove(container_id: str) -> None:
        """Remove a Docker container by its ID.

        Args:
            container_id (str): The ID of the container to remove.

        Raises:
            Exception: If the container cannot be removed.
        """
        client = get_docker_client()

        get_logger(__name__).debug(f"Removing container with ID: {container_id}")

        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
        except Exception as e:
            raise Exception(
                f"Failed to remove container {container_id}. Error: {str(e)}"
            ) from e

    @staticmethod
    def start_container(container: Container) -> None:
        """Start a Docker container.

        Args:
            container (Container): The Docker container instance to start.
        """
        container.start()
