from __future__ import annotations

from typing import Any, List, cast

from svs_core.db.models import ServiceModel, ServiceStatus
from svs_core.docker.container import DockerContainerManager
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


class Service(ServiceModel):
    """Service class representing a service in the system."""

    objects = ServiceModel.objects

    class Meta:  # noqa: D106
        proxy = True

    @property
    def env_variables(self) -> List[EnvVariable]:  # noqa: D102
        env_dict = self.env or {}
        return [EnvVariable(key=key, value=value) for key, value in env_dict.items()]

    @property
    def port_mappings(self) -> List[ExposedPort]:  # noqa: D102
        ports_list = self.exposed_ports or []
        result = []
        for port in ports_list:
            container_port = port.get("container")
            if container_port is not None:  # container_port is required
                result.append(
                    ExposedPort(
                        container_port=int(container_port),
                        host_port=(
                            int(port["host"]) if port.get("host") is not None else None
                        ),
                    )
                )
        return result

    @property
    def volume_mappings(self) -> List[Volume]:  # noqa: D102
        volumes_list = self.volumes or []
        result = []
        for volume in volumes_list:
            container_path = volume.get("container")
            if container_path is not None:  # container_path is required
                result.append(
                    Volume(
                        container_path=str(container_path),
                        host_path=(
                            str(volume["host"])
                            if volume.get("host") is not None
                            else None
                        ),
                    )
                )
        return result

    @property
    def label_list(self) -> List[Label]:  # noqa: D102
        labels_dict = self.labels or {}
        return [Label(key=key, value=value) for key, value in labels_dict.items()]

    @property
    def healthcheck_config(self) -> Healthcheck | None:  # noqa: D102
        healthcheck_dict = self.healthcheck or {}
        if not healthcheck_dict or "test" not in healthcheck_dict:
            return None

        return Healthcheck(
            test=healthcheck_dict.get("test", []),
            interval=healthcheck_dict.get("interval"),
            timeout=healthcheck_dict.get("timeout"),
            retries=healthcheck_dict.get("retries"),
            start_period=healthcheck_dict.get("start_period"),
        )

    @property
    def template_obj(self) -> Template:  # noqa: D102
        return cast(Template, Template.objects.get(id=self.template_id))

    @property
    def status(self) -> ServiceStatus:  # noqa: D102
        container = DockerContainerManager.get_container(self.container_id)
        if container is None:
            return ServiceStatus.CREATED

        return ServiceStatus.from_str(container.status)

    @property
    def user_obj(self) -> User:  # noqa: D102
        return cast(User, User.objects.get(id=self.user_id))

    def to_env_dict(self) -> dict[str, str]:
        """Convert EnvVariable list to dictionary format."""
        return {env.key: env.value for env in self.env_variables}

    def to_ports_list(self) -> list[dict[str, Any]]:
        """Convert ExposedPort list to list of dictionaries format."""
        return [
            {"container": port.container_port, "host": port.host_port}
            for port in self.port_mappings
        ]

    def to_volumes_list(self) -> list[dict[str, Any]]:
        """Convert Volume list to list of dictionaries format."""
        return [
            {"container": vol.container_path, "host": vol.host_path}
            for vol in self.volume_mappings
        ]

    def to_labels_dict(self) -> dict[str, str]:
        """Convert Label list to dictionary format."""
        return {label.key: label.value for label in self.label_list}

    def to_healthcheck_dict(self) -> dict[str, Any] | None:
        """Convert Healthcheck object to dictionary format."""
        if not self.healthcheck_config:
            return None

        result: dict[str, Any] = {"test": self.healthcheck_config.test}
        if self.healthcheck_config.interval:
            result["interval"] = self.healthcheck_config.interval
        if self.healthcheck_config.timeout:
            result["timeout"] = self.healthcheck_config.timeout
        if self.healthcheck_config.retries:
            result["retries"] = self.healthcheck_config.retries
        if self.healthcheck_config.start_period:
            result["start_period"] = self.healthcheck_config.start_period
        return result

    def __str__(self) -> str:
        env_vars = [f"{env.key}={env.value}" for env in self.env_variables]
        ports = [
            f"{port.container_port}:{port.host_port}" for port in self.port_mappings
        ]
        volumes = [
            f"{vol.container_path}:{vol.host_path or 'None'}"
            for vol in self.volume_mappings
        ]
        labels = [f"{label.key}={label.value}" for label in self.label_list]

        healthcheck_str = "None"
        if self.healthcheck_config:
            test_str = " ".join(self.healthcheck_config.test)
            healthcheck_str = f"test='{test_str}'"

        return (
            f"Service(id={self.id}, name={self.name}, domain={self.domain}, "
            f"container_id={self.container_id}, image={self.image}, "
            f"exposed_ports=[{', '.join(ports)}], "
            f"env=[{', '.join(env_vars)}], "
            f"volumes=[{', '.join(volumes)}], "
            f"command={self.command}, "
            f"healthcheck={healthcheck_str}, "
            f"labels=[{', '.join(labels)}], "
            f"args={self.args}, networks={self.networks}, "
            f"status={self.status}, exit_code={self.exit_code})"
        )

    @classmethod
    def create_from_template(
        cls,
        name: str,
        template_id: int,
        user: User,
        domain: str | None = None,
        override_env: dict[str, str] | None = None,
        override_ports: list[dict[str, Any]] | None = None,
        override_volumes: list[dict[str, Any]] | None = None,
        override_command: str | None = None,
        override_healthcheck: dict[str, Any] | None = None,
        override_labels: dict[str, str] | None = None,
        override_args: list[str] | None = None,
        networks: list[str] | None = None,
    ) -> Service:
        """Creates a service from an existing template with overrides.

        Args:
            name (str): The name of the service.
            user (User): The user who owns this service.
            domain (str, optional): The domain for this service.
            override_env (dict, optional): Environment variables to override template defaults.
            override_ports (list[dict], optional): Exposed ports to override template defaults.
            override_volumes (list[dict], optional): Volume mappings to override template defaults.
            override_command (str, optional): Command to override template default.
            override_healthcheck (dict, optional): Healthcheck configuration to override template default.
            override_labels (dict, optional): Container labels to override template defaults.
            override_args (list, optional): Command arguments to override template defaults.
            networks (list, optional): Networks to connect to.

        Returns:
            Service: The created service instance.

        Raises:
            ValueError: If name is empty or template_id doesn't correspond to an existing template.
        """
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise ValueError(f"Template with ID {template_id} does not exist")

        env = {var.key: var.value for var in template.env_variables}
        if override_env:
            env.update(override_env)

        exposed_ports = [
            {"container": port.container_port, "host": port.host_port}
            for port in template.exposed_ports
        ]
        for override in override_ports or []:
            existing = next(
                (
                    p
                    for p in exposed_ports
                    if p["container"] == override.get("container")
                ),
                None,
            )
            if existing:
                existing.update(override)
            else:
                exposed_ports.append(override)

        volumes = [
            {"container": vol.container_path, "host": vol.host_path}
            for vol in template.volumes
        ]
        for override in override_volumes or []:
            # TODO: fix later ;)
            existing = next(
                (v for v in volumes if v["container"] == override.get("container")),
                None,
            )  # type: ignore
            if existing:
                existing.update(override)
            else:
                volumes.append(override)

        labels = {label.key: label.value for label in template.label_list}
        if override_labels:
            labels.update(override_labels)

        healthcheck: dict[str, Any] | None = None
        if template.healthcheck_config:
            healthcheck = {"test": template.healthcheck_config.test}
            if template.healthcheck_config.interval:
                healthcheck["interval"] = template.healthcheck_config.interval
            if template.healthcheck_config.timeout:
                healthcheck["timeout"] = template.healthcheck_config.timeout
            if template.healthcheck_config.retries:
                healthcheck["retries"] = template.healthcheck_config.retries
            if template.healthcheck_config.start_period:
                healthcheck["start_period"] = template.healthcheck_config.start_period

        # TODO: allow partial overrides / merge
        if override_healthcheck:
            healthcheck = override_healthcheck

        command_to_use = (
            override_command if override_command is not None else template.start_cmd
        )
        args_to_use = override_args

        if args_to_use is None and template.args:
            args_to_use = template.args.copy()

        if args_to_use is not None:
            for i, arg in enumerate(args_to_use):
                if not isinstance(arg, str):
                    args_to_use[i] = str(arg)

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
            command=command_to_use,
            healthcheck=healthcheck,
            labels=labels | {"svs_user": user.name},
            args=args_to_use,
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
        exposed_ports: list[dict[str, Any]] | None = None,
        env: dict[str, str] | None = None,
        volumes: list[dict[str, Any]] | None = None,
        command: str | None = None,
        healthcheck: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        args: list[str] | None = None,
        networks: list[str] | None = None,
        exit_code: int | None = None,
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
            exposed_ports (list[dict], optional): Exposed ports, defaults to template.default_ports if not provided.
            env (dict, optional): Environment variables, defaults to template.default_env if not provided.
            volumes (list[dict], optional): Volume mappings, defaults to template.default_volumes if not provided.
            command (str, optional): Command to run in the container, defaults to template.start_cmd if not provided.
            healthcheck (dict, optional): Healthcheck configuration, defaults to template.healthcheck if not provided.
            labels (dict, optional): Container labels, defaults to template.labels if not provided.
            args (list, optional): Command arguments, defaults to template.args if not provided.
            networks (list, optional): Networks to connect to.
            exit_code (int, optional): Container exit code.

        Returns:
            Service: The created service instance.

        Raises:
            ValueError: If name is empty or template_id doesn't correspond to an existing template.
        """
        if not name:
            raise ValueError("Service name cannot be empty")

        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            raise ValueError(f"Template with ID {template_id} does not exist")

        if image is None:
            image = template.image

        if exposed_ports is None:
            template_ports = template.exposed_ports
            exposed_ports = [
                {"container": port.container_port, "host": port.host_port}
                for port in template_ports
            ]
        else:
            for port in exposed_ports:
                if not isinstance(port, dict) or "container" not in port:
                    raise ValueError(f"Invalid port specification: {port}")
                if "container" in port and port["container"] is not None:
                    try:
                        port["container"] = int(port["container"])
                    except (ValueError, TypeError):
                        raise ValueError(f"Container port must be an integer: {port}")
                if "host" in port and port["host"] is not None:
                    try:
                        port["host"] = int(port["host"])
                    except (ValueError, TypeError):
                        raise ValueError(f"Host port must be an integer: {port}")

        if env is None:
            template_env = template.env_variables
            env = {var.key: var.value for var in template_env}
        else:
            if not isinstance(env, dict):
                raise ValueError(f"Environment variables must be a dictionary: {env}")
            for key, value in env.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Environment variable key and value must be strings: {key}={value}"
                    )

        if volumes is None:
            template_volumes = template.volumes
            volumes = [
                {"container": vol.container_path, "host": vol.host_path}
                for vol in template_volumes
            ]
        else:
            for volume in volumes:
                if not isinstance(volume, dict) or "container" not in volume:
                    raise ValueError(f"Invalid volume specification: {volume}")
                if "container" in volume and volume["container"] is not None:
                    if not isinstance(volume["container"], str):
                        raise ValueError(f"Container path must be a string: {volume}")
                if "host" in volume and volume["host"] is not None:
                    if not isinstance(volume["host"], str):
                        raise ValueError(f"Host path must be a string: {volume}")

        if command is None:
            command = template.start_cmd

        if healthcheck is None and template.healthcheck_config:
            healthcheck_obj = template.healthcheck_config
            healthcheck = {"test": healthcheck_obj.test}

            if healthcheck_obj.interval:
                healthcheck["interval"] = healthcheck_obj.interval
            if healthcheck_obj.timeout:
                healthcheck["timeout"] = healthcheck_obj.timeout
            if healthcheck_obj.retries:
                healthcheck["retries"] = healthcheck_obj.retries
            if healthcheck_obj.start_period:
                healthcheck["start_period"] = healthcheck_obj.start_period

        elif healthcheck is not None:
            if not isinstance(healthcheck, dict):
                raise ValueError(f"Healthcheck must be a dictionary: {healthcheck}")
            if "test" not in healthcheck:
                raise ValueError("Healthcheck must contain a 'test' field")
            if not isinstance(healthcheck["test"], list):
                raise ValueError(
                    f"Healthcheck test must be a list of strings: {healthcheck['test']}"
                )

        if labels is None:
            template_labels = template.label_list
            labels = {label.key: label.value for label in template_labels}
        else:
            if not isinstance(labels, dict):
                raise ValueError(f"Labels must be a dictionary: {labels}")
            for key, value in labels.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Label key and value must be strings: {key}={value}"
                    )

        if args is None:
            args = template.args

        # Generate ports and volumes
        for port in exposed_ports:
            if "host" not in port or port["host"] is None:
                port["host"] = SystemPortManager.find_free_port()

        for volume in volumes:
            if "host" not in volume or volume["host"] is None:
                volume["host"] = SystemVolumeManager.generate_free_volume(
                    user
                ).as_posix()

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
            exit_code=exit_code,
        )

        system_labels = [Label(key="service_id", value=str(service_instance.id))]

        if service_instance.domain:
            system_labels.append(Label(key="caddy", value=service_instance.domain))

            if service_instance.exposed_ports:
                http_ports = [port for port in service_instance.port_mappings]

                if http_ports:
                    upstreams = ", ".join(
                        f"{{upstreams {port.container_port}}}" for port in http_ports
                    )
                    if upstreams:
                        system_labels.append(Label(key="upstreams", value=upstreams))

        model_labels = service_instance.label_list

        all_labels = system_labels + model_labels

        if not service_instance.image:
            raise ValueError("Service must have an image specified")

        args_to_use = None
        if service_instance.args:
            args_to_use = []
            for arg in service_instance.args:
                if not isinstance(arg, str):
                    args_to_use.append(str(arg))
                else:
                    args_to_use.append(arg)

        get_logger(__name__).info(f"Creating service '{name}'")

        container = DockerContainerManager.create_container(
            name=name,
            image=service_instance.image,
            command=service_instance.command,
            args=args_to_use,
            labels=all_labels,
            ports={
                port["container"]: port["host"]
                for port in service_instance.to_ports_list()
            },
        )

        service_instance.container_id = container.id
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
