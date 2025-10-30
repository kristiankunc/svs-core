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

    def __str__(self) -> str:
        dockerfile_head = self.dockerfile.splitlines()[:5] if self.dockerfile else []

        return (
            f"Template(id={self.id}, name={self.name}, type={self.type}, image={self.image}, "
            f"dockerfile_head={dockerfile_head}, description={self.description}, "
            f"default_env={[var.__str__() for var in self.default_env]}, "
            f"default_ports={[port.__str__() for port in self.default_ports]}, "
            f"default_volumes={[vol.__str__() for vol in self.default_volumes]}, "
            f"start_cmd={self.start_cmd}, "
            f"healthcheck={self.healthcheck}, "
            f"labels={[label.__str__() for label in self.labels]}, "
            f"args={self.args})"
        )

    @classmethod
    def create(
        cls,
        name: str,
        type: TemplateType = TemplateType.IMAGE,
        image: str | None = None,
        dockerfile: str | None = None,
        description: str | None = None,
        default_env: list[EnvVariable] | None = None,
        default_ports: list[ExposedPort] | None = None,
        default_volumes: list[Volume] | None = None,
        start_cmd: str | None = None,
        healthcheck: Healthcheck | None = None,
        labels: list[Label] | None = None,
        args: list[str] | None = None,
    ) -> Template:
        """Creates a new template with all supported attributes.

        Args:
            name (str): The name of the template.
            type (TemplateType, optional): The type of the template (image or build). Defaults to TemplateType.IMAGE.
            image (str | None, optional): The Docker image name (if type is image). Defaults to None.
            dockerfile (str | None, optional): The Dockerfile content (if type is build). Defaults to None.
            description (str | None, optional): A description of the template. Defaults to None.
            default_env (list[EnvVariable] | None, optional): Default environment variables. Defaults to None.
            default_ports (list[ExposedPort] | None, optional): Default exposed ports. Defaults to None.
            default_volumes (list[Volume] | None, optional): Default volume bindings. Defaults to None.
            start_cmd (str | None, optional): The default start command. Defaults to None.
            healthcheck (Healthcheck | None, optional): The healthcheck configuration. Defaults to None.
            labels (list[Label] | None, optional): Default Docker labels. Defaults to None.
            args (list[str] | None, optional): Default arguments for the container. Defaults to None.

        Returns:
            Template: A new Template instance.

        Raises:
            ValueError: If any of the provided values are invalid.
        """

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
            for var in default_env:
                if not isinstance(var.key, str) or not isinstance(var.value, str):
                    raise ValueError(
                        f"Default environment keys and values must be strings: {var.key}={var.value}"
                    )
                if not var.key:
                    raise ValueError("Default environment keys cannot be empty")

        # Validate default_ports
        if default_ports is not None:
            for port in default_ports:
                # host_port can be None (meaning any available host port), but container_port must be an int
                if port.host_port is not None and not isinstance(port.host_port, int):
                    raise ValueError(
                        f"Port host_port must be an integer or None: {port}"
                    )
                if not isinstance(port.container_port, int):
                    raise ValueError(f"Port container_port must be an integer: {port}")
                # If host_port is provided, it must be positive
                if port.host_port is not None and port.host_port <= 0:
                    raise ValueError(
                        f"Port host_port must be a positive integer when provided: {port}"
                    )
                if port.container_port <= 0:
                    raise ValueError(
                        f"Port container_port must be a positive integer: {port}"
                    )

        # Validate default_volumes
        if default_volumes is not None:
            for volume in default_volumes:
                if not isinstance(volume.container_path, str):
                    raise ValueError(
                        f"Volume container path must be a string: {volume}"
                    )
                if volume.host_path is not None and not isinstance(
                    volume.host_path, str
                ):
                    raise ValueError(f"Volume host path must be a string: {volume}")
                if not volume.container_path:
                    raise ValueError("Volume container path cannot be empty")

        # Validate start_cmd
        if start_cmd is not None and not isinstance(start_cmd, str):
            raise ValueError(f"Start command must be a string: {start_cmd}")

        # Validate healthcheck
        if healthcheck is not None and len(healthcheck.test) == 0:
            raise ValueError("Healthcheck must contain a 'test' field")

        # Validate labels
        if labels is not None:
            for label in labels:
                if not isinstance(label.key, str) or not isinstance(label.value, str):
                    raise ValueError(
                        f"Label keys and values must be strings: {label.key}={label.value}"
                    )
                if not label.key:
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

        # Process default_env: handle both flat dict and list formats
        default_env_data = data.get("default_env", [])
        if isinstance(default_env_data, dict):
            # Convert flat dict to list of dicts format: {"KEY": "value"} -> [{"KEY": "value"}]
            default_env_list = [{k: v} for k, v in default_env_data.items()]
        else:
            default_env_list = default_env_data

        # Process default_ports: handle both formats
        # Format 1: [{"host_port": 8080, "container_port": 80}] (single key-value format)
        # Format 2: [{"host": 8080, "container": 80}] (named field format)
        default_ports_data = data.get("default_ports", [])
        default_ports_list = []
        for port_data in default_ports_data:
            if isinstance(port_data, dict):
                # Handle named field format: {"host": 8080, "container": 80}
                if "host" in port_data and "container" in port_data:
                    default_ports_list.append(
                        ExposedPort(
                            host_port=port_data["host"],
                            container_port=port_data["container"],
                        )
                    )
                # Handle single key-value format: {8080: 80}
                elif len(port_data) == 1:
                    host_port = next(iter(port_data))
                    container_port = port_data[host_port]
                    default_ports_list.append(
                        ExposedPort(host_port=host_port, container_port=container_port)
                    )
                else:
                    raise ValueError(
                        f"Invalid port specification: {port_data}. "
                        "Must contain either 'host' and 'container' fields or be a single key-value pair."
                    )

        # Process default_volumes: handle both formats
        # Format 1: [{"host_path": "/host", "container_path": "/container"}]
        # Format 2: [{"host": "/host", "container": "/container"}]
        default_volumes_data = data.get("default_volumes", [])
        default_volumes_list = []
        for vol_data in default_volumes_data:
            if isinstance(vol_data, dict):
                # Handle named field format: {"host": "/host", "container": "/container"}
                if "host" in vol_data and "container" in vol_data:
                    default_volumes_list.append(
                        Volume(
                            host_path=vol_data["host"],
                            container_path=vol_data["container"],
                        )
                    )
                # Handle single key-value format: {"/host": "/container"}
                elif len(vol_data) == 1:
                    host_path = next(iter(vol_data))
                    container_path = vol_data[host_path]
                    default_volumes_list.append(
                        Volume(host_path=host_path, container_path=container_path)
                    )
                else:
                    raise ValueError(
                        f"Invalid volume specification: {vol_data}. "
                        "Must contain either 'host' and 'container' fields or be a single key-value pair."
                    )

        # Process labels: handle both flat dict and list formats
        labels_data = data.get("labels", [])
        if isinstance(labels_data, dict):
            # Convert flat dict to list of dicts format: {"KEY": "value"} -> [{"KEY": "value"}]
            labels_list = [{k: v} for k, v in labels_data.items()]
        else:
            labels_list = labels_data

        # Delegate to create method for further validation
        template: "Template" = cls.create(
            name=data.get("name", ""),
            type=template_type,
            image=data.get("image"),
            dockerfile=data.get("dockerfile"),
            description=data.get("description"),
            default_env=EnvVariable.from_dict_array(default_env_list),
            default_ports=default_ports_list,
            default_volumes=default_volumes_list,
            start_cmd=data.get("start_cmd"),
            healthcheck=Healthcheck.from_dict(data.get("healthcheck")),
            labels=Label.from_dict_array(labels_list),
            args=data.get("args"),
        )

        return template

    def delete(self) -> None:
        """Deletes the template and associated Docker image if applicable.

        Raises:
            Exception: If the template is associated with existing services.
        """

        from svs_core.docker.service import Service

        services = Service.objects.filter(template=self)

        if len(services) > 0:
            raise Exception(
                f"Cannot delete template {self.name} as it is associated with existing services."
            )

        if self.type == TemplateType.IMAGE and self.image:
            DockerImageManager.remove(self.image)

        super().delete()
