from typing import TYPE_CHECKING, Optional

from docker.models.containers import Container

from svs_core.docker.base import get_docker_client
from svs_core.docker.json_properties import EnvVariable, ExposedPort, Label, Volume
from svs_core.shared.logger import get_logger
from svs_core.shared.volumes import SystemVolumeManager
from svs_core.users.system import SystemUserManager
from svs_core.users.user import User

if TYPE_CHECKING:
    from svs_core.docker.service import Service


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
            PermissionError: If there are permission issues creating the container.
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
                    owner_account = User.objects.get(name=owner)
                    if not volume.host_path.startswith(
                        (
                            SystemVolumeManager.BASE_PATH / str(owner_account.id)
                        ).as_posix()
                    ):
                        raise PermissionError(
                            f"Volume host path '{volume.host_path}' is outside the allowed directory for user '{owner}'."
                        )
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
            docker_env_vars["PGID"] = str(SystemUserManager.get_gid("svs-admins"))
        else:
            create_kwargs["user"] = (
                f"{str(SystemUserManager.get_system_uid_gid(owner)[0])}:{str(SystemUserManager.get_gid('svs-admins'))}"
            )

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

    @staticmethod
    def has_config_changed(container: Container, service: "Service") -> bool:
        """Check if the container's configuration has changed.

        Compares the current configuration of the Docker container with the
        desired configuration defined in the service definition.

        Args:
            container (Container): The Docker container instance.
            service (Service): The service definition to compare against.

        Returns:
            bool: True if the configuration has changed.
        """

        container.reload()
        container_attrs = container.attrs

        # Check image
        if container_attrs["Config"]["Image"] != service.image:
            return True

        # Check command
        container_command = " ".join(container_attrs["Config"]["Cmd"] or [])
        service_command = service.command or ""
        if container_command != service_command:
            return True

        # Check environment variables
        container_env = set(container_attrs["Config"]["Env"] or [])
        service_env = set(
            f"{env_var.key}={env_var.value}"
            for env_var in service.environment_variables
        )
        if container_env != service_env:
            return True

        # Check exposed ports
        container_ports = set(container_attrs["NetworkSettings"]["Ports"] or {})
        service_ports = set(f"{port.container_port}/tcp" for port in service.ports)
        if container_ports != service_ports:
            return True

        # Check volumes
        container_mounts = set(
            mount["Destination"] for mount in container_attrs["Mounts"] or []
        )
        service_volumes = set(volume.container_path for volume in service.volumes)
        if container_mounts != service_volumes:
            return True

        return False

    @staticmethod
    def recreate_container(container: Container, service: "Service") -> Container:
        """Recreate a Docker container.

        Stops and removes the existing container, then creates a new one with the
        updated configuration from the service definition.

        Args:
            container (Container): The existing Docker container instance to recreate.
            service (Service): The service definition with the target configuration.

        Returns:
            Container: The newly created Docker container instance.

        Raises:
            ServiceOperationException: If the container cannot be properly stopped or removed.
        """
        from svs_core.shared.exceptions import ServiceOperationException

        get_logger(__name__).info(
            f"Recreating container '{container.name}' (ID: {container.id}) with updated configuration"
        )

        was_running = container.status == "running"

        # Stop the container if it's running
        if was_running:
            try:
                get_logger(__name__).debug(
                    f"Stopping container '{container.name}' before recreation"
                )
                container.stop()
            except Exception as e:
                get_logger(__name__).error(
                    f"Failed to stop container '{container.name}': {str(e)}"
                )
                raise ServiceOperationException(
                    f"Failed to stop container {container.id}: {str(e)}"
                ) from e

        # Remove the old container
        try:
            get_logger(__name__).debug(
                f"Removing old container '{container.name}' (ID: {container.id})"
            )
            container.remove(force=True)
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to remove container '{container.name}': {str(e)}"
            )
            raise ServiceOperationException(
                f"Failed to remove container {container.id}: {str(e)}"
            ) from e

        # Create a new container with the updated configuration
        try:
            new_container = DockerContainerManager.create_container(
                name=container.name,
                image=service.image,
                owner=service.user.name,
                command=service.command,
                args=service.args,
                labels=service.labels,
                ports=service.exposed_ports,
                volumes=service.volumes,
                environment_variables=service.env,
            )

            get_logger(__name__).info(
                f"Successfully recreated container with ID: {new_container.id}"
            )

            return new_container
        except Exception as e:
            get_logger(__name__).error(f"Failed to create new container: {str(e)}")
            raise ServiceOperationException(
                f"Failed to recreate container: {str(e)}"
            ) from e
