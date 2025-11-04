from typing import Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client
from svs_core.docker.json_properties import ExposedPort, Label, Volume
from svs_core.shared.logger import get_logger


class DockerContainerManager:
    """Class for managing Docker containers."""

    @staticmethod
    def create_container(
        name: str,
        image: str,
        command: str | None = None,
        args: list[str] | None = None,
        labels: list[Label] = [],
        ports: list[ExposedPort] | None = None,
        volumes: list[Volume] | None = None,
    ) -> Container:
        """Create a Docker container.

        Args:
            name (str): The name of the container.
            image (str): The Docker image to use.
            command (str | None): The command to run in the container.
            args (list[str] | None): The arguments for the command.
            labels (list[Label]): List of labels to assign to the container.
            ports (list[ExposedPort] | None): List of ports to expose.
            volumes (list[Volume] | None): List of volumes to mount.

        Returns:
            Container: The created Docker container instance.

        Raises:
            ValueError: If volume paths are not properly specified.
        """
        client = get_docker_client()

        full_command = None
        if command and args:
            full_command = f"{command} {' '.join(args)}"
        elif command:
            full_command = command
        elif args:
            full_command = " ".join(args)

        docker_ports = {}
        if ports:
            for port in ports:
                docker_ports[f"{port.container_port}/tcp"] = port.host_port

        volume_mounts: list[str] = []
        if volumes:
            for volume in volumes:
                if volume.host_path and volume.container_path:
                    volume_mounts.append(f"{volume.host_path}:{volume.container_path}")
                else:
                    raise ValueError(
                        "Both host_path and container_path must be provided for Volume."
                    )

        get_logger(__name__).debug(
            f"Creating container with config: name={name}, image={image}, command={full_command}, labels={labels}, ports={docker_ports}, volumes={volume_mounts}"
        )

        create_kwargs = {
            "image": image,
            "name": name,
            "detach": True,
            "labels": {label.key: label.value for label in labels},
            "ports": docker_ports or {},
            "volumes": volume_mounts or [],
        }

        if full_command is not None:
            create_kwargs["command"] = full_command

        return client.containers.create(**create_kwargs)

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
