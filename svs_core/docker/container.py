from typing import Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client
from svs_core.docker.json_properties import EnvVariable, ExposedPort, Label, Volume
from svs_core.shared.logger import get_logger
from svs_core.users.system import SystemUserManager


class DockerContainerManager:
    """Class for managing Docker containers."""

    @staticmethod
    def create_container(
        name: str,
        image: str,
        owner: str,
        command: str | None = None,
        args: list[str] | None = None,
        labels: list[Label] | None = None,
        ports: list[ExposedPort] | None = None,
        volumes: list[Volume] | None = None,
        environment_variables: list[EnvVariable] | None = None,
    ) -> Container:
        """Create a Docker container.

        Args:
            name (str): The name of the container.
            image (str): The Docker image to use.
            owner (str): The system user who will own the container.
            command (str | None): The command to run in the container.
            args (list[str] | None): The arguments for the command.
            labels (list[Label]): List of labels to assign to the container.
            ports (list[ExposedPort] | None): List of ports to expose.
            volumes (list[Volume] | None): List of volumes to mount.
            environment_variables (list[EnvVariable] | None): List of environment variables to set.

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

        docker_env_vars = {}
        if environment_variables:
            for env_var in environment_variables:
                docker_env_vars[env_var.key] = env_var.value

        volume_mounts: list[str] = []
        if volumes:
            for volume in volumes:
                if volume.host_path and volume.container_path:
                    volume_mounts.append(
                        f"{volume.host_path}:{volume.container_path}:rw"
                    )
                else:
                    raise ValueError(
                        "Both host_path and container_path must be provided for Volume."
                    )

        if labels is None:
            labels = []

        get_logger(__name__).debug(
            f"Creating container with config: name={name}, image={image}, command={full_command}, labels={labels}, ports={docker_ports}, volumes={volume_mounts}"
        )

        create_kwargs: dict[str, object] = {}

        if "lscr.io/linuxserver/" in image or "linuxserver/" in image:
            # For LinuxServer.io images - https://docs.linuxserver.io/general/understanding-puid-and-pgid/
            docker_env_vars["PUID"] = str(
                SystemUserManager.get_system_uid_gid(owner)[0]
            )
        else:
            user_data = SystemUserManager.get_system_uid_gid(owner)
            create_kwargs["user"] = f"{user_data[0]}:{user_data[1]}"

        create_kwargs.update(
            {
                "image": image,
                "name": name,
                "detach": True,
                "labels": {label.key: label.value for label in labels},
                "ports": docker_ports or {},
                "volumes": volume_mounts or [],
                "environment": docker_env_vars or {},
            }
        )

        if full_command is not None:
            create_kwargs["command"] = full_command

        try:
            container = client.containers.create(**create_kwargs)
            get_logger(__name__).info(
                f"Successfully created container '{name}' with image '{image}'"
            )

            return container

        except Exception as e:
            get_logger(__name__).error(f"Failed to create container '{name}': {str(e)}")
            raise

    @staticmethod
    def connect_to_network(container: Container, network_name: str) -> None:
        """Connect a Docker container to a specified network.

        Args:
            container (Container): The Docker container instance.
            network_name (str): The name of the network to connect to.
        """
        get_logger(__name__).debug(
            f"Connecting container '{container.name}' to network '{network_name}'"
        )

        client = get_docker_client()

        try:
            network = client.networks.get(network_name)
            network.connect(container)
            get_logger(__name__).info(
                f"Connected container '{container.name}' to network '{network_name}'"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to connect container '{container.name}' to network '{network_name}': {str(e)}"
            )
            raise

    @staticmethod
    def get_container(container_id: str) -> Optional[Container]:
        """Retrieve a Docker container by its ID.

        Args:
            container_id (str): The ID of the container to retrieve.

        Returns:
            Optional[Container]: The Docker container instance if found, otherwise None.
        """
        get_logger(__name__).debug(f"Retrieving container with ID: {container_id}")

        client = get_docker_client()
        try:
            container = client.containers.get(container_id)
            get_logger(__name__).debug(
                f"Container '{container_id}' found with status: {container.status}"
            )
            return container
        except Exception as e:
            get_logger(__name__).debug(
                f"Container '{container_id}' not found: {str(e)}"
            )
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
        get_logger(__name__).debug(f"Removing container with ID: {container_id}")

        client = get_docker_client()

        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
            get_logger(__name__).info(
                f"Successfully removed container '{container_id}'"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to remove container '{container_id}': {str(e)}"
            )
            raise Exception(
                f"Failed to remove container {container_id}. Error: {str(e)}"
            ) from e

    @staticmethod
    def start_container(container: Container) -> None:
        """Start a Docker container.

        Args:
            container (Container): The Docker container instance to start.
        """
        get_logger(__name__).debug(
            f"Starting container '{container.name}' (ID: {container.id})"
        )

        try:
            container.start()
            get_logger(__name__).info(
                f"Successfully started container '{container.name}'"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to start container '{container.name}': {str(e)}"
            )
            raise
