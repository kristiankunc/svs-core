from typing import Any, List

from svs_core.db.models import OrmBase, ServiceModel, TemplateModel
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.template import Template
from svs_core.users.user import User


class Service(OrmBase):
    _model_cls = ServiceModel

    def __init__(self, model: ServiceModel, **_: Any):
        super().__init__(model)
        self._model: ServiceModel = model

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def container_id(self) -> str | None:
        return self._model.container_id

    @property
    def image(self) -> str | None:
        return self._model.image

    @property
    def domain(self) -> str | None:
        return self._model.domain

    @property
    def env(self) -> List[EnvVariable]:
        env_dict = self._model.env or {}
        return [EnvVariable(key=key, value=value) for key, value in env_dict.items()]

    @property
    def exposed_ports(self) -> List[ExposedPort]:
        ports_list = self._model.exposed_ports or []
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
    def volumes(self) -> List[Volume]:
        volumes_list = self._model.volumes or []
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
    def command(self) -> str | None:
        return self._model.command

    @property
    def labels(self) -> List[Label]:
        labels_dict = self._model.labels or {}
        return [Label(key=key, value=value) for key, value in labels_dict.items()]

    @property
    def args(self) -> list[str]:
        return self._model.args or []

    @property
    def healthcheck(self) -> Healthcheck | None:
        healthcheck_dict = self._model.healthcheck or {}
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
    def networks(self) -> list[str]:
        return self._model.networks or []

    @property
    def status(self) -> str | None:
        return self._model.status

    @property
    def exit_code(self) -> int | None:
        return self._model.exit_code

    @property
    def template(self) -> Template:
        return Template(model=self._model.template)

    @property
    def user(self) -> User:
        return User(model=self._model.user)

    def to_env_dict(self) -> dict[str, str]:
        """Convert EnvVariable list to dictionary format."""
        return {env.key: env.value for env in self.env}

    def to_ports_list(self) -> list[dict[str, Any]]:
        """Convert ExposedPort list to list of dictionaries format."""
        return [
            {"container": port.container_port, "host": port.host_port}
            for port in self.exposed_ports
        ]

    def to_volumes_list(self) -> list[dict[str, Any]]:
        """Convert Volume list to list of dictionaries format."""
        return [
            {"container": vol.container_path, "host": vol.host_path}
            for vol in self.volumes
        ]

    def to_labels_dict(self) -> dict[str, str]:
        """Convert Label list to dictionary format."""
        return {label.key: label.value for label in self.labels}

    def to_healthcheck_dict(self) -> dict[str, Any] | None:
        """Convert Healthcheck object to dictionary format."""
        if not self.healthcheck:
            return None

        result: dict[str, Any] = {"test": self.healthcheck.test}
        if self.healthcheck.interval:
            result["interval"] = self.healthcheck.interval
        if self.healthcheck.timeout:
            result["timeout"] = self.healthcheck.timeout
        if self.healthcheck.retries:
            result["retries"] = self.healthcheck.retries
        if self.healthcheck.start_period:
            result["start_period"] = self.healthcheck.start_period
        return result

    def __str__(self) -> str:
        env_vars = [f"{env.key}={env.value}" for env in self.env]
        ports = [
            f"{port.container_port}:{port.host_port}" for port in self.exposed_ports
        ]
        volumes = [
            f"{vol.container_path}:{vol.host_path or 'None'}" for vol in self.volumes
        ]
        labels = [f"{label.key}={label.value}" for label in self.labels]

        healthcheck_str = "None"
        if self.healthcheck:
            test_str = " ".join(self.healthcheck.test)
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
    async def create_from_template(
        cls,
        name: str,
        template: Template,
        user_id: int,
        domain: str | None = None,
        override_env: dict[str, str] | None = None,
        override_ports: list[dict[str, Any]] | None = None,
        override_volumes: list[dict[str, Any]] | None = None,
        override_command: str | None = None,
        override_healthcheck: dict[str, Any] | None = None,
        override_labels: dict[str, str] | None = None,
        override_args: list[str] | None = None,
        networks: list[str] | None = None,
    ) -> "Service":
        """
        Creates a new service from an existing template with optional overrides.

        Args:
            name (str): The name of the service.
            template (Template): The template to use.
            user_id (int): The ID of the user who owns this service.
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
        """
        # Convert template values to model format
        env = {var.key: var.value for var in template.default_env}
        if override_env:
            env.update(override_env)

        exposed_ports = [
            {"container": port.container_port, "host": port.host_port}
            for port in template.default_ports
        ]
        if override_ports:
            # Replace with overrides (could be more sophisticated to merge)
            exposed_ports = override_ports

        volumes = [
            {"container": vol.container_path, "host": vol.host_path}
            for vol in template.default_volumes
        ]
        if override_volumes:
            # Replace with overrides (could be more sophisticated to merge)
            volumes = override_volumes

        labels = {label.key: label.value for label in template.labels}
        if override_labels:
            labels.update(override_labels)

        healthcheck: dict[str, Any] | None = None
        if template.healthcheck:
            healthcheck = {"test": template.healthcheck.test}
            if template.healthcheck.interval:
                healthcheck["interval"] = template.healthcheck.interval
            if template.healthcheck.timeout:
                healthcheck["timeout"] = template.healthcheck.timeout
            if template.healthcheck.retries:
                healthcheck["retries"] = template.healthcheck.retries
            if template.healthcheck.start_period:
                healthcheck["start_period"] = template.healthcheck.start_period
        if override_healthcheck:
            healthcheck = override_healthcheck

        # Process command and args to make sure they are properly formatted
        command_to_use = (
            override_command if override_command is not None else template.start_cmd
        )
        args_to_use = override_args

        if args_to_use is None and template.args:
            # Create a copy of the list to avoid modifying the template's args
            args_to_use = template.args.copy()

        # Validate args is a list of strings if provided
        if args_to_use is not None:
            for i, arg in enumerate(args_to_use):
                if not isinstance(arg, str):
                    args_to_use[i] = str(arg)

        # Use the regular create method with the prepared values
        return await cls.create(
            name=name,
            template_id=template.id,
            user_id=user_id,
            domain=domain,
            image=template.image,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            command=command_to_use,
            healthcheck=healthcheck,
            labels=labels,
            args=args_to_use,
            networks=networks,
        )

    @classmethod
    async def create(
        cls,
        name: str,
        template_id: int,
        user_id: int,
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
        status: str | None = "created",
        exit_code: int | None = None,
    ) -> "Service":
        """
        Creates a new service with all supported attributes.
        Values not explicitly provided will be inherited from the template where applicable.

        Args:
            name (str): The name of the service.
            template_id (int): The ID of the template to use.
            user_id (int): The ID of the user who owns this service.
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
            status (str, optional): Initial service status, defaults to "created".
            exit_code (int, optional): Container exit code.

        Returns:
            Service: The created service instance.

        Raises:
            ValueError: If name is empty or template_id doesn't correspond to an existing template.
        """
        name = name.strip()
        if not name:
            raise ValueError("Service name cannot be empty")

        # Get template to inherit values from
        from tortoise.exceptions import DoesNotExist

        try:
            template_model = await TemplateModel.get(id=template_id)
            template = Template(model=template_model)
        except DoesNotExist:
            raise ValueError(f"Template with ID {template_id} does not exist")

        # Inherit values from template if not provided
        if image is None:
            image = template.image

        # Handle ExposedPorts with proper JSON wrapper objects
        if exposed_ports is None:
            # Get ports from template and convert to dict format expected by the model
            template_ports = template.default_ports
            exposed_ports = [
                {"container": port.container_port, "host": port.host_port}
                for port in template_ports
            ]
        else:
            # Validate the provided ports list
            for port in exposed_ports:
                if not isinstance(port, dict) or "container" not in port:
                    raise ValueError(f"Invalid port specification: {port}")
                # Ensure container port is an integer
                if "container" in port and port["container"] is not None:
                    try:
                        port["container"] = int(port["container"])
                    except (ValueError, TypeError):
                        raise ValueError(f"Container port must be an integer: {port}")
                # Ensure host port is an integer or None
                if "host" in port and port["host"] is not None:
                    try:
                        port["host"] = int(port["host"])
                    except (ValueError, TypeError):
                        raise ValueError(f"Host port must be an integer: {port}")

        # Handle EnvVariables with proper JSON wrapper objects
        if env is None:
            # Get environment variables from template and convert to dict format expected by the model
            template_env = template.default_env
            env = {var.key: var.value for var in template_env}
        else:
            # Validate the provided env dict
            if not isinstance(env, dict):
                raise ValueError(f"Environment variables must be a dictionary: {env}")
            for key, value in env.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Environment variable key and value must be strings: {key}={value}"
                    )

        # Handle Volumes with proper JSON wrapper objects
        if volumes is None:
            # Get volumes from template and convert to dict format expected by the model
            template_volumes = template.default_volumes
            volumes = [
                {"container": vol.container_path, "host": vol.host_path}
                for vol in template_volumes
            ]
        else:
            # Validate the provided volumes list
            for volume in volumes:
                if not isinstance(volume, dict) or "container" not in volume:
                    raise ValueError(f"Invalid volume specification: {volume}")
                # Ensure container path is a string
                if "container" in volume and volume["container"] is not None:
                    if not isinstance(volume["container"], str):
                        raise ValueError(f"Container path must be a string: {volume}")
                # Ensure host path is a string or None
                if "host" in volume and volume["host"] is not None:
                    if not isinstance(volume["host"], str):
                        raise ValueError(f"Host path must be a string: {volume}")

        if command is None:
            command = template.start_cmd

        # Handle Healthcheck with proper JSON wrapper object
        if healthcheck is None and template.healthcheck:
            # Get healthcheck from template and convert to dict format expected by the model
            healthcheck_obj = template.healthcheck
            healthcheck = {"test": healthcheck_obj.test}

            # Add optional fields if they exist
            if healthcheck_obj.interval:
                healthcheck["interval"] = healthcheck_obj.interval
            if healthcheck_obj.timeout:
                healthcheck["timeout"] = healthcheck_obj.timeout
            if healthcheck_obj.retries:
                healthcheck["retries"] = healthcheck_obj.retries
            if healthcheck_obj.start_period:
                healthcheck["start_period"] = healthcheck_obj.start_period
        elif healthcheck is not None:
            # Validate the provided healthcheck dict
            if not isinstance(healthcheck, dict):
                raise ValueError(f"Healthcheck must be a dictionary: {healthcheck}")
            if "test" not in healthcheck:
                raise ValueError("Healthcheck must contain a 'test' field")
            if not isinstance(healthcheck["test"], list):
                raise ValueError(
                    f"Healthcheck test must be a list of strings: {healthcheck['test']}"
                )

        # Handle Labels with proper JSON wrapper objects
        if labels is None:
            # Get labels from template and convert to dict format expected by the model
            template_labels = template.labels
            labels = {label.key: label.value for label in template_labels}
        else:
            # Validate the provided labels dict
            if not isinstance(labels, dict):
                raise ValueError(f"Labels must be a dictionary: {labels}")
            for key, value in labels.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Label key and value must be strings: {key}={value}"
                    )

        if args is None:
            args = template.args

        model = await ServiceModel.create(
            name=name,
            template_id=template_id,
            user_id=user_id,
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
            status=status,
            exit_code=exit_code,
        )
        service_instance = cls(model=model)

        # Create system labels that should always be present
        system_labels = [Label(key="service_id", value=str(service_instance.id))]

        # Add domain label for caddy if domain is specified
        if service_instance.domain:
            system_labels.append(Label(key="caddy", value=service_instance.domain))

            # Add upstreams label for caddy service discovery if ports are exposed
            if service_instance.exposed_ports:
                # Filter out ports that aren't HTTP/HTTPS standard ports
                http_ports = [
                    port
                    for port in service_instance.exposed_ports
                    if port.container_port in (80, 443)
                ]

                if http_ports:
                    upstreams = ", ".join(
                        f"{{upstreams {port.container_port}}}" for port in http_ports
                    )
                    if upstreams:
                        system_labels.append(Label(key="upstreams", value=upstreams))

        # Use service_instance.labels which is already a List[Label]
        model_labels = service_instance.labels

        # Combine system labels with model labels
        all_labels = system_labels + model_labels

        # Docker container creation with only supported parameters
        # NOTE: In the future, DockerContainerManager.create_container should be updated
        # to handle env, ports, volumes, and healthcheck parameters
        if not service_instance.image:
            raise ValueError("Service must have an image specified")

        # Ensure args is a list of strings or None
        args_to_use = None
        if service_instance.args:
            args_to_use = []
            for arg in service_instance.args:
                if not isinstance(arg, str):
                    args_to_use.append(str(arg))
                else:
                    args_to_use.append(arg)

        container = DockerContainerManager.create_container(
            name=name,
            image=service_instance.image,  # We've verified it's not None above
            command=service_instance.command,
            args=args_to_use,
            labels=all_labels,
        )

        model.container_id = container.id
        await model.save()

        return service_instance

    async def start(self) -> None:
        """Start the service's Docker container."""
        if not self.container_id:
            raise ValueError("Service does not have a container ID")

        container = DockerContainerManager.get_container(self.container_id)
        if not container:
            raise ValueError(f"Container with ID {self.container_id} not found")

        container.start()
        self._model.status = "running"
        await self._model.save()
