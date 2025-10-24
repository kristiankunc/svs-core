from __future__ import annotations

from typing import Any, List, cast

from svs_core.db.models import TemplateModel, TemplateType
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.shared.logger import get_logger


class Template(TemplateModel):
    """Template class representing a Docker template in the system."""

    class Meta:  # noqa: D106
        proxy = True

    @property
    def env_variables(self) -> List[EnvVariable]:  # noqa: D102
        env_dict = self.default_env or {}
        return [EnvVariable(key=key, value=value) for key, value in env_dict.items()]

    @property
    def exposed_ports(self) -> List[ExposedPort]:  # noqa: D102
        ports_list = self.default_ports or []
        result = []
        for port in ports_list:
            container_port = port.get("container")
            if container_port is not None:
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
    def volumes(self) -> List[Volume]:  # noqa: D102
        volumes_list = self.default_volumes or []
        return [
            Volume(
                container_path=str(volume["container"]),
                host_path=(
                    str(volume["host"]) if volume.get("host") is not None else None
                ),
            )
            for volume in volumes_list
        ]

    @property
    def healthcheck_config(self) -> Healthcheck | None:
        """Returns the healthcheck configuration for the template, if any."""
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
    def label_list(self) -> List[Label]:
        """Returns the list of labels for the template."""
        labels_dict = self.labels or {}
        return [Label(key=key, value=value) for key, value in labels_dict.items()]

    @property
    def arguments(self) -> list[str]:
        """Returns the list of build arguments for the template."""
        return self.args or []

    def __str__(self) -> str:
        env_vars = [f"{env.key}={env.value}" for env in self.env_variables]
        ports = [
            f"{port.container_port}:{port.host_port}" for port in self.exposed_ports
        ]
        volumes = [
            f"{vol.container_path}:{vol.host_path or 'None'}" for vol in self.volumes
        ]
        labels = [f"{label.key}={label.value}" for label in self.label_list]

        healthcheck_str = "None"
        if self.healthcheck_config:
            test_str = " ".join(self.healthcheck_config.test)
            healthcheck_str = f"test='{test_str}'"

        return (
            f"Template(id={self.id}, name={self.name}, type={self.type}, image={self.image}, "
            f"dockerfile={self.dockerfile}, description={self.description}, "
            f"default_env=[{', '.join(env_vars)}], "
            f"default_ports=[{', '.join(ports)}], "
            f"default_volumes=[{', '.join(volumes)}], "
            f"start_cmd={self.start_cmd}, "
            f"healthcheck={healthcheck_str}, "
            f"labels=[{', '.join(labels)}], "
            f"args={self.arguments})"
        )

    @classmethod
    def create(
        cls,
        name: str,
        type: TemplateType = TemplateType.IMAGE,
        image: str | None = None,
        dockerfile: str | None = None,
        description: str | None = None,
        default_env: dict[str, str] | None = None,
        default_ports: list[dict[str, Any]] | None = None,
        default_volumes: list[dict[str, Any]] | None = None,
        start_cmd: str | None = None,
        healthcheck: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        args: list[str] | None = None,
    ) -> Template:
        """Creates a new template with all supported attributes."""
        # Validate name
        if not name:
            raise ValueError("Template name cannot be empty")

        # Validate type-specific requirements
        if type == TemplateType.IMAGE:
            if not image:
                raise ValueError("Image type templates must specify an image")
        elif type == TemplateType.BUILD:
            if not dockerfile:
                raise ValueError("Build type templates must specify a dockerfile")

        # Validate image format if provided
        if image is not None:
            if not image:
                raise ValueError("Image cannot be empty if provided")

        # Validate dockerfile if provided
        if dockerfile is not None and not dockerfile.strip():
            raise ValueError("Dockerfile cannot be empty if provided")

        # Validate default_env
        if default_env is not None:
            for key, value in default_env.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Default environment keys and values must be strings: {key}={value}"
                    )
                if not key:
                    raise ValueError("Default environment keys cannot be empty")

        # Validate default_ports
        if default_ports is not None:
            for port in default_ports:
                if not isinstance(port, dict):
                    raise ValueError(f"Port specification must be a dictionary: {port}")
                if "container" not in port:
                    raise ValueError(
                        f"Port specification must contain a 'container' field: {port}"
                    )
                if (
                    not isinstance(port["container"], int)
                    and port["container"] is not None
                ):
                    raise ValueError(
                        f"Container port must be an integer or None: {port}"
                    )
                if (
                    "host" in port
                    and port["host"] is not None
                    and not isinstance(port["host"], int)
                ):
                    raise ValueError(
                        f"Host port must be an integer or None if specified: {port}"
                    )

        # Validate default_volumes
        if default_volumes is not None:
            for volume in default_volumes:
                if not isinstance(volume, dict):
                    raise ValueError(
                        f"Volume specification must be a dictionary: {volume}"
                    )
                if "container" not in volume:
                    raise ValueError(
                        f"Volume specification must contain a 'container' field: {volume}"
                    )
                if not isinstance(volume["container"], str):
                    raise ValueError(f"Container path must be a string: {volume}")
                if (
                    "host" in volume
                    and volume["host"] is not None
                    and not isinstance(volume["host"], str)
                ):
                    raise ValueError(
                        f"Host path must be a string or None if specified: {volume}"
                    )

        # Validate start_cmd
        if start_cmd is not None and not isinstance(start_cmd, str):
            raise ValueError(f"Start command must be a string: {start_cmd}")

        # Validate healthcheck
        if healthcheck is not None:
            required_keys = ["test"]
            for key in required_keys:
                if key not in healthcheck:
                    raise ValueError(f"Healthcheck must contain a '{key}' field")

        # Validate labels
        if labels is not None:
            for key, value in labels.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(
                        f"Label keys and values must be strings: {key}={value}"
                    )
                if not key:
                    raise ValueError("Label keys cannot be empty")

        # Validate args
        if args is not None:
            if not isinstance(args, list):
                raise ValueError(f"Arguments must be a list of strings: {args}")
            for arg in args:
                if not isinstance(arg, str):
                    raise ValueError(f"Argument must be a string: {arg}")
                if not arg:
                    raise ValueError("Arguments cannot be empty strings")

        get_logger(__name__).debug(
            f"Creating template with name={name}, type={type}, image={image}, dockerfile={dockerfile}, "
            f"description={description}, default_env={default_env}, default_ports={default_ports}, "
            f"default_volumes={default_volumes}, start_cmd={start_cmd}, healthcheck={healthcheck}, "
            f"labels={labels}, args={args}"
        )

        template = cls.objects.create(
            name=name,
            type=type,
            image=image,
            dockerfile=dockerfile,
            description=description,
            default_env=default_env,
            default_ports=default_ports,
            default_volumes=default_volumes,
            start_cmd=start_cmd,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
        )

        # TODO: remove type gymnastics
        if type == TemplateType.IMAGE and image is not None:
            # Parse the image name to handle tags correctly
            if ":" in image:
                image_name, tag = image.split(":", 1)
                if not DockerImageManager.exists(image_name, tag):
                    DockerImageManager.pull(image_name, tag)
            else:
                if not DockerImageManager.exists(image):
                    DockerImageManager.pull(image, "latest")

        elif type == TemplateType.BUILD and dockerfile is not None:
            print(f"Building image for template {name} from dockerfile")
            DockerImageManager.build_from_dockerfile(name, dockerfile)

        return cast(Template, template)

    @classmethod
    def import_from_json(cls, data: dict[str, Any]) -> Template:
        """Creates a Template instance from a JSON/dict object.

        Relies on theexisting create factory method.

        Args:
            data (dict[str, Any]): The JSON data dictionary containing template attributes.

        Returns:
            Template: A new Template instance created from the JSON data.

        Raises:
            ValueError: If the data is invalid or missing required fields.
        """
        # Validate input
        if not isinstance(data, dict):
            raise ValueError(
                f"Template import data must be a dictionary, got {type(data)}"
            )

        # Validate required fields
        if "name" not in data:
            raise ValueError("Template import data must contain a 'name' field")

        # Validate template type
        template_type = data.get("type", "image")
        try:
            template_type = TemplateType(template_type)
        except ValueError:
            valid_types = [t.value for t in TemplateType]
            raise ValueError(
                f"Invalid template type: {template_type}. Must be one of: {valid_types}"
            )

        # Validate type-specific fields
        if template_type == TemplateType.IMAGE and "image" not in data:
            raise ValueError(
                "Image type templates must specify an 'image' field in import data"
            )
        elif template_type == TemplateType.BUILD and "dockerfile" not in data:
            raise ValueError(
                "Build type templates must specify a 'dockerfile' field in import data"
            )

        # Delegate to create method for further validation
        template: "Template" = cls.create(
            name=data.get("name", ""),
            type=template_type,
            image=data.get("image"),
            dockerfile=data.get("dockerfile"),
            description=data.get("description"),
            default_env=data.get("default_env"),
            default_ports=data.get("default_ports"),
            default_volumes=data.get("default_volumes"),
            start_cmd=data.get("start_cmd"),
            healthcheck=data.get("healthcheck"),
            labels=data.get("labels"),
            args=data.get("args"),
        )

        return template
