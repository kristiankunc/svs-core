from __future__ import annotations

import time

from pathlib import Path
from typing import Any, List, TypeVar, Union, cast

from svs_core.db.models import ServiceModel, ServiceStatus, TemplateType
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.template import Template
from svs_core.shared.logger import get_logger
from svs_core.shared.ports import SystemPortManager
from svs_core.shared.volumes import SystemVolumeManager
from svs_core.users.user import User

Mergeable = Union[EnvVariable, ExposedPort, Volume, Label]
T = TypeVar("T", bound=Mergeable)


class Service(ServiceModel):
    """Service class representing a service in the system."""

    objects = ServiceModel.objects

    # Constants for rebuild stop retry logic
    MAX_STOP_RETRIES = 3
    STOP_RETRY_DELAY_SECONDS = 1

    class Meta:  # noqa: D106
        proxy = True

    @property
    def template_obj(self) -> Template:  # noqa: D102
        return cast(Template, Template.objects.get(id=self.template_id))

    @property
    def status(self) -> ServiceStatus:  # noqa: D102
        container = DockerContainerManager.get_container(self.container_id)
        if container is None:
            return ServiceStatus.CREATED

        return ServiceStatus.from_str(container.status)

    def __str__(self) -> str:  # noqa: D105
        return (
            f"Service(id={self.id}, name={self.name}, template_id={self.template_id}, "
            f"user_id={self.user_id}, domain={self.domain}, container_id={self.container_id}, "
            f"image={self.image}, "
            f"exposed_ports={[port.__str__() for port in self.exposed_ports]}, "
            f"env={[var.__str__() for var in self.env]}, "
            f"volumes={[vol.__str__() for vol in self.volumes]}, "
            f"command={self.command}, "
            f"healthcheck={self.healthcheck}, "
            f"labels={[label.__str__() for label in self.labels]}, "
            f"args={self.args}, "
            f"status={self.status})"
        )

    @staticmethod
    def _merge_overrides(base: List[T], overrides: List[T]) -> List[T]:
        """Merges two lists of key-value pairs.

        If either list is empty, returns the non-empty one. Otherwise,
        overrides in the second list will replace those in the first list
        based on matching identifiers:
        - For ExposedPort: merge by container_port (value)
        - For Volume: merge by container_path (value)
        - For others: merge by key

        Non-matching items from both lists are included.

        Args:
            base (List[T]): The base list of key-value pairs.
            overrides (List[T]): The list of key-value pairs to override.

        Returns:
            List[T]: The merged list of key-value pairs.
        """
        # Handle empty lists
        if not base:
            return overrides if overrides else []
        if not overrides:
            return base

        from svs_core.docker.json_properties import ExposedPort, Volume

        # Determine merge key based on type
        def get_merge_key(item: T) -> Any:
            if isinstance(item, ExposedPort):
                return item.container_port  # Merge by container_port (value)
            elif isinstance(item, Volume):
                return item.container_path  # Merge by container_path (value)
            else:
                return item.key  # Default: merge by key

        merged: dict[Any, T] = {get_merge_key(item): item for item in base}

        for override in overrides:
            merged[get_merge_key(override)] = override

        return list(merged.values())

    @classmethod
    def create_from_template(
        cls,
        name: str,
        template_id: int,
        user: User,
        domain: str | None = None,
        override_env: list[EnvVariable] | None = None,
        override_ports: list[ExposedPort] | None = None,
        override_volumes: list[Volume] | None = None,
        override_command: str | None = None,
        override_healthcheck: Healthcheck | None = None,
        override_labels: list[Label] | None = None,
        override_args: list[str] | None = None,
        networks: list[str] | None = None,
    ) -> Service:
        """Creates a service from an existing template with overrides.

        Arguments that inherit from the KeyValue class (EnvVariable, Volume, ExposedPort, Label) allow partial merging and overriding. Other arguments completely replace the template's default values.

        Args:
            name (str): The name of the service.
            template_id (int): The ID of the template to use.
            user (User): The user who owns this service.
            domain (str, optional): The domain for this service.
            override_env (list[EnvVariable], optional): Environment variables to override.
            override_ports (list[ExposedPort], optional): Exposed ports to override.
            override_volumes (list[Volume], optional): Volumes to override.
            override_command (str, optional): Command to run in the container.
            override_healthcheck (Healthcheck, optional): Healthcheck configuration.
            override_labels (list[Label], optional): Container labels to override.
            override_args (list[str], optional): Command arguments to override.
            networks (list[str], optional): Networks to connect to.

        Returns:
            Service: The created service instance.

        Raises:
            ValueError: If name is empty or template_id doesn't correspond to an existing template.
        """

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise ValueError(f"Template with ID {template_id} does not exist")

        if not name:
            raise ValueError("Service name cannot be empty")

        env = (
            cls._merge_overrides(template.default_env, override_env)
            if override_env
            else template.default_env
        )
        exposed_ports = (
            cls._merge_overrides(template.default_ports, override_ports)
            if override_ports
            else template.default_ports
        )
        volumes = (
            cls._merge_overrides(template.default_volumes, override_volumes)
            if override_volumes
            else template.default_volumes
        )
        labels = (
            cls._merge_overrides(template.labels, override_labels)
            if override_labels
            else template.labels
        )
        healthcheck = (
            override_healthcheck if override_healthcheck else template.healthcheck
        )
        command = override_command if override_command else template.start_cmd
        args = override_args if override_args else template.args

        get_logger(__name__).info(
            f"Creating service '{name}' from template '{template.name}'"
        )

        return cls.create(
            name=name,
            template_id=template.id,
            user=user,
            domain=domain,
            image=template.image,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            command=command,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
            networks=networks,
        )

    @classmethod
    def create(
        cls,
        name: str,
        template_id: int,
        user: User,
        domain: str | None = None,
        container_id: str | None = None,
        image: str | None = None,
        exposed_ports: list[ExposedPort] | None = None,
        env: list[EnvVariable] | None = None,
        volumes: list[Volume] | None = None,
        command: str | None = None,
        healthcheck: Healthcheck | None = None,
        labels: list[Label] | None = None,
        args: list[str] | None = None,
        networks: list[str] | None = None,
    ) -> Service:
        """Creates a new service with all supported attributes.

        Values not explicitly provided will be inherited from the template where
        applicable.

        Args:
            name (str): The name of the service.
            template_id (int): The ID of the template to use.
            user (User): The user who owns this service.
            domain (str, optional): The domain for this service.
            container_id (str, optional): The ID of an existing container.
            image (str, optional): Docker image to use, defaults to template.image if not provided.
            exposed_ports (list[ExposedPort], optional): Exposed ports, defaults to template.default_ports if not provided.
            env (list[EnvVariable], optional): Environment variables, defaults to template.default_env if not provided.
            volumes (list[Volume], optional): Volume mappings, defaults to template.default_volumes if not provided.
            command (str, optional): Command to run in the container, defaults to template.start_cmd if not provided.
            healthcheck (Healthcheck, optional): Healthcheck configuration, defaults to template.healthcheck if not provided.
            labels (list[Label], optional): Container labels, defaults to template.labels if not provided.
            args (list[str], optional): Command arguments, defaults to template.args if not provided.
            networks (list[str], optional): Networks to connect to.

        Returns:
            Service: The created service instance.

        Raises:
            ValueError: If name is empty or template_id doesn't correspond to an existing template.
        """
        # Input validation
        if not name:
            raise ValueError("Service name cannot be empty")

        if not isinstance(name, str):
            raise ValueError(f"Service name must be a string: {name}")

        if not isinstance(template_id, int):
            raise ValueError(f"Template ID must be an integer: {template_id}")

        if template_id <= 0:
            raise ValueError(f"Template ID must be positive: {template_id}")

        if domain is not None and not isinstance(domain, str):
            raise ValueError(f"Domain must be a string: {domain}")

        if container_id is not None and not isinstance(container_id, str):
            raise ValueError(f"Container ID must be a string: {container_id}")

        if image is not None and not isinstance(image, str):
            raise ValueError(f"Image must be a string: {image}")

        if command is not None and not isinstance(command, str):
            raise ValueError(f"Command must be a string: {command}")

        if networks is not None:
            if not isinstance(networks, list):
                raise ValueError(f"Networks must be a list: {networks}")
            for net in networks:
                if not isinstance(net, str):
                    raise ValueError(f"Each network must be a string: {net}")

        # Validate exposed_ports
        if exposed_ports is not None:
            if not isinstance(exposed_ports, list):
                raise ValueError(f"Exposed ports must be a list: {exposed_ports}")
            for port in exposed_ports:
                if not isinstance(port, ExposedPort):
                    raise ValueError(
                        f"Each port must be an ExposedPort instance: {port}"
                    )
                if not isinstance(port.container_port, int) or port.container_port <= 0:
                    raise ValueError(
                        f"Container port must be a positive integer: {port.container_port}"
                    )

        # Validate env
        if env is not None:
            if not isinstance(env, list):
                raise ValueError(f"Environment variables must be a list: {env}")
            for var in env:
                if not isinstance(var, EnvVariable):
                    raise ValueError(
                        f"Each environment variable must be an EnvVariable instance: {var}"
                    )
                if not var.key or not isinstance(var.key, str):
                    raise ValueError(
                        f"Environment variable key must be a non-empty string: {var.key}"
                    )
                if not isinstance(var.value, str):
                    raise ValueError(
                        f"Environment variable value must be a string: {var.value}"
                    )

        # Validate volumes
        if volumes is not None:
            if not isinstance(volumes, list):
                raise ValueError(f"Volumes must be a list: {volumes}")
            for vol in volumes:
                if not isinstance(vol, Volume):
                    raise ValueError(f"Each volume must be a Volume instance: {vol}")
                if not vol.container_path or not isinstance(vol.container_path, str):
                    raise ValueError(
                        f"Volume container path must be a non-empty string: {vol.container_path}"
                    )
                if vol.host_path is not None and not isinstance(vol.host_path, str):
                    raise ValueError(
                        f"Volume host path must be a string: {vol.host_path}"
                    )

        # Validate labels
        if labels is not None:
            if not isinstance(labels, list):
                raise ValueError(f"Labels must be a list: {labels}")
            for label in labels:
                if not isinstance(label, Label):
                    raise ValueError(f"Each label must be a Label instance: {label}")
                if not label.key or not isinstance(label.key, str):
                    raise ValueError(
                        f"Label key must be a non-empty string: {label.key}"
                    )
                if not isinstance(label.value, str):
                    raise ValueError(f"Label value must be a string: {label.value}")

        # Validate healthcheck
        if healthcheck is not None and not isinstance(healthcheck, Healthcheck):
            raise ValueError(
                f"Healthcheck must be a Healthcheck instance: {healthcheck}"
            )

        # Validate args
        if args is not None:
            if not isinstance(args, list):
                raise ValueError(f"Arguments must be a list: {args}")
            for arg in args:
                if not isinstance(arg, str):
                    raise ValueError(f"Each argument must be a string: {arg}")

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise ValueError(f"Template with ID {template_id} does not exist")

        # Validate image for IMAGE templates
        if template.type == TemplateType.IMAGE and not image:
            raise ValueError("Service must have an image specified")

        if template.type == TemplateType.IMAGE:
            if not DockerImageManager.exists(template.image):
                DockerImageManager.pull(template.image)

        # Use template defaults if not provided
        if image is None:
            image = template.image

        if exposed_ports is None:
            exposed_ports = list(template.default_ports)

        if env is None:
            env = list(template.default_env)

        if volumes is None:
            volumes = list(template.default_volumes)

        if command is None:
            command = template.start_cmd

        if healthcheck is None:
            healthcheck = template.healthcheck

        if labels is None:
            labels = list(template.labels)

        if args is None:
            args = list(template.args) if template.args else []

        # Generate free ports and volumes if needed
        for port in exposed_ports:
            if port.host_port is None:
                port.host_port = SystemPortManager.find_free_port()

        for volume in volumes:
            if volume.host_path is None:
                volume.host_path = SystemVolumeManager.generate_free_volume(
                    user
                ).as_posix()

        labels.append(Label(key="svs_user", value=user.name))

        # Create service instance
        service_instance = cls.objects.create(
            name=name,
            template_id=template_id,
            user_id=user.id,
            domain=domain,
            container_id=container_id,
            image=image,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            command=command,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
            networks=networks,
        )

        system_labels = [Label(key="service_id", value=str(service_instance.id))]

        if service_instance.domain:
            system_labels.append(Label(key="caddy", value=service_instance.domain))
            system_labels.append(
                Label(key="caddy.reverse_proxy", value="{{upstreams 80}}")
            )

        model_labels = list(service_instance.labels)
        all_labels = system_labels + model_labels

        # Update service with all labels (system + model)
        service_instance.labels = all_labels

        get_logger(__name__).info(f"Creating service '{name}'")

        for default_content in service_instance.template.default_contents:
            true_host_path = SystemVolumeManager.find_host_path(
                Path(default_content.location), service_instance.volumes
            )
            if true_host_path and not true_host_path.exists():
                get_logger(__name__).debug(
                    f"Adding default content to volume at '{true_host_path}'"
                )
                default_content.write_to_host(true_host_path, user.name)

        if template.type == TemplateType.IMAGE:
            container = DockerContainerManager.create_container(
                name=f"svs-{service_instance.id}",
                image=service_instance.image,
                owner=user.name,
                command=service_instance.command,
                args=service_instance.args,
                labels=all_labels,
                ports=service_instance.exposed_ports,
                volumes=service_instance.volumes,
                environment_variables=service_instance.env,
            )

            service_instance.container_id = container.id

            DockerContainerManager.connect_to_network(container, user.name)

            if "caddy" in [label.key for label in all_labels]:
                DockerContainerManager.connect_to_network(container, "caddy")

        service_instance.save()

        return cast(Service, service_instance)

    def start(self) -> None:
        """Start the service's Docker container."""
        if not self.container_id:
            raise ValueError("Service does not have a container ID")

        container = DockerContainerManager.get_container(self.container_id)
        if not container:
            raise ValueError(f"Container with ID {self.container_id} not found")

        get_logger(__name__).info(
            f"Starting service '{self.name}' with container ID '{self.container_id}'"
        )

        container.start()
        self.save()

    def stop(self) -> None:
        """Stop the service's Docker container."""
        if not self.container_id:
            raise ValueError("Service does not have a container ID")

        container = DockerContainerManager.get_container(self.container_id)
        if not container:
            raise ValueError(f"Container with ID {self.container_id} not found")

        get_logger(__name__).info(
            f"Stopping service '{self.name}' with container ID '{self.container_id}'"
        )

        container.stop()
        self.save()

    def delete(self) -> None:
        """Delete the service and its Docker container."""
        if self.container_id:
            container = DockerContainerManager.get_container(self.container_id)
            if container:
                get_logger(__name__).info(
                    f"Deleting container '{self.container_id}' for service '{self.name}'"
                )
                container.remove(force=True)

        if self.template.type == TemplateType.BUILD:
            if self.image and DockerImageManager.exists(self.image):
                get_logger(__name__).info(
                    f"Deleting built image '{self.image}' for service '{self.name}'"
                )
                DockerImageManager.delete(self.image)

        volumes = self.volumes
        for volume in volumes:
            if volume.host_path:
                SystemVolumeManager.delete_volume(Path(volume.host_path))

        get_logger(__name__).info(f"Deleting service '{self.name}'")

        super().delete()

    def get_logs(self, tail: int = 1000) -> str:
        """Retrieve the logs of the service's Docker container.

        Args:
            tail (int): Number of lines from the end of the logs to retrieve.

        Returns:
            str: The logs of the container as a string.
        """
        if not self.container_id:
            raise ValueError("Service does not have a container ID")

        container = DockerContainerManager.get_container(self.container_id)
        if not container:
            raise ValueError(f"Container with ID {self.container_id} not found")

        get_logger(__name__).debug(
            f"Retrieving logs for service '{self.name}' with container ID '{self.container_id}'"
        )

        logs = container.logs(tail=tail)
        return cast(str, logs.decode("utf-8"))

    def build(self, source_path: Path) -> None:
        """Build the service's Docker from a Dockerfile.

        This method is used when the template type is DOCKERFILE. It builds the Docker image
        using the Dockerfile found in the specified source path.

        Args:
            source_path (Path): The path to the directory containing the Dockerfile.

        Raises:
            ValueError: If the source path does not exist, is not a directory, or if the template type is not BUILD.
        """
        # Validate source path exists and is a directory
        if not source_path.exists():
            raise ValueError(f"Source path does not exist: {source_path}")
        if not source_path.is_dir():
            raise ValueError(f"Source path is not a directory: {source_path}")

        if self.template.type != TemplateType.BUILD:
            raise ValueError("Service template type is not BUILD; cannot build image.")

        production_image_name = f"svs-{self.id}:latest"
        build_image_name = f"{self.template.name.lower()}-{self.id}:{int(time.time())}"

        get_logger(__name__).info(
            f"Building image '{build_image_name}' on-demand for service '{self.name}' in path '{source_path}', with ENV vars: {[env.__str__() for env in self.env]}"
        )

        DockerImageManager.build_from_dockerfile(
            build_image_name,
            self.template.dockerfile,
            path_to_copy=source_path,
            build_args={env.key: env.value for env in self.env},
        )

        get_logger(__name__).debug(
            f"Successfully built image '{build_image_name}' for service '{self.name}'"
        )

        if not self.image:
            DockerImageManager.rename(build_image_name, production_image_name)

            self.image = production_image_name

            container = DockerContainerManager.create_container(
                name=f"svs-{self.id}",
                image=self.image,
                owner=self.user.name,
                command=self.command,
                args=self.args,
                labels=self.labels,
                ports=self.exposed_ports,
                volumes=self.volumes,
            )

            self.container_id = container.id

            DockerContainerManager.connect_to_network(container, self.user.name)

        else:
            container = DockerContainerManager.get_container(self.container_id)
            if not container:
                raise ValueError(f"Container with ID {self.container_id} not found")

            get_logger(__name__).debug(
                f"Rebuilding image for service '{self.name}' (container '{self.container_id}') to '{production_image_name}'"
            )

            # Capture the running state before making changes
            was_running = self.status == ServiceStatus.RUNNING

            # Stop the container if it's running
            if was_running:
                self.stop()

                # Wait for the container to actually stop after stop() is called
                # Docker's stop operation can take time (graceful shutdown with SIGTERM, then SIGKILL)
                for attempt in range(self.MAX_STOP_RETRIES):
                    container = DockerContainerManager.get_container(self.container_id)
                    if not container or container.status != "running":
                        break

                    # Wait before next check to give container time to stop
                    if attempt < self.MAX_STOP_RETRIES - 1:
                        get_logger(__name__).warning(
                            f"Container {self.container_id} still running after stop() - waiting (attempt {attempt + 1}/{self.MAX_STOP_RETRIES})"
                        )
                        time.sleep(self.STOP_RETRY_DELAY_SECONDS)
                    else:
                        get_logger(__name__).error(
                            f"Container {self.container_id} failed to stop after {self.MAX_STOP_RETRIES} attempts"
                        )
                        raise RuntimeError(
                            f"Failed to stop container {self.container_id} after {self.MAX_STOP_RETRIES} attempts"
                        )

            # Remove the old container so we can create a new one with the updated image
            get_logger(__name__).debug(
                f"Removing old container '{self.container_id}' before recreating with new image"
            )
            DockerContainerManager.remove(self.container_id)

            # Remove the old production image before renaming (cleanup)
            try:
                get_logger(__name__).debug(
                    f"Removing old production image '{production_image_name}' before rename"
                )
                DockerImageManager.remove(production_image_name)
            except Exception as e:
                # Catch broad Exception as DockerImageManager.remove() itself raises Exception
                # for various docker-related errors (image not found, in use, etc.)
                # If the image doesn't exist or can't be removed, just log a warning
                get_logger(__name__).warning(
                    f"Could not remove old production image '{production_image_name}': {str(e)}"
                )

            # Rename the newly built image to the production name
            DockerImageManager.rename(build_image_name, production_image_name)

            # Update the image reference
            self.image = production_image_name

            # Create a new container with the updated image
            new_container = DockerContainerManager.create_container(
                name=f"svs-{self.id}",
                image=self.image,
                owner=self.user.name,
                command=self.command,
                args=self.args,
                labels=self.labels,
                ports=self.exposed_ports,
                volumes=self.volumes,
            )

            self.container_id = new_container.id

            DockerContainerManager.connect_to_network(new_container, self.user.name)

            # Start the new container if it was running before
            if was_running:
                self.start()

        self.save()
