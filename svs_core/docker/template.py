from __future__ import annotations

from typing import Any, List, cast

from svs_core.db.models import TemplateModel, TemplateType
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import (
    DefaultContent,
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
            f"Template(id={self.id}, name={self.name}, type={self.type}, "
            f"image={self.image}, dockerfile_head={dockerfile_head}, "
            f"description={self.description}, "
            f"default_env={[var.__str__() for var in self.default_env]}, "
            f"default_ports={[port.__str__() for port in self.default_ports]}, "
            f"default_volumes={[vol.__str__() for vol in self.default_volumes]}, "
            f"default_contents={[content.__str__() for content in self.default_contents]}, "
            f"start_cmd={self.start_cmd}, healthcheck={self.healthcheck}, "
            f"labels={[label.__str__() for label in self.labels]}, args={self.args})"
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
        default_contents: list[DefaultContent] | None = None,
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
            default_contents (list[DefaultContent] | None, optional): Default file contents to create in the container. Defaults to None.
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

        # Validate default_contents
        if default_contents is not None:
            for content in default_contents:
                if not isinstance(content.location, str):
                    raise ValueError(
                        f"Default content location must be a string: {content}"
                    )
                if not isinstance(content.content, str):
                    raise ValueError(f"Default content must be a string: {content}")
                if not content.location:
                    raise ValueError("Default content location cannot be empty")

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

        get_logger(__name__).info(f"Creating template '{name}' of type '{type}'")
        get_logger(__name__).debug(
            f"Template details: image={image}, dockerfile={'set' if dockerfile else 'None'}, "
            f"description={description}, default_env={default_env}, default_ports={default_ports}, "
            f"default_volumes={default_volumes}, default_contents={default_contents}, start_cmd={start_cmd}, healthcheck={healthcheck}, "
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
            default_contents=default_contents,
            start_cmd=start_cmd,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
        )

        if type == TemplateType.IMAGE and image is not None:
            if not DockerImageManager.exists(image):
                get_logger(__name__).debug(
                    f"Image '{image}' not found locally, pulling from registry"
                )
                DockerImageManager.pull(image)

        elif type == TemplateType.BUILD and dockerfile is not None:
            get_logger(__name__).debug(
                f"Template '{name}' created as BUILD type. Image will be built on-demand when services are created."
            )

        get_logger(__name__).info(f"Successfully created template '{name}'")
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
        get_logger(__name__).info(
            f"Importing template from JSON: {data.get('name', 'unnamed')}"
        )

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

        # Process default_env: should be a list of {"key": ..., "value": ...} dicts
        default_env_data = data.get("default_env", [])
        if not isinstance(default_env_data, list):
            raise ValueError(
                f"default_env must be a list, got {type(default_env_data).__name__}"
            )
        default_env_list = default_env_data

        # Process default_ports: strict parsing according to schema
        # Schema format: [{"host": 8080, "container": 80}] with "container" required and "host" optional
        default_ports_data = data.get("default_ports", [])
        default_ports_list = []
        for port_data in default_ports_data:
            if not isinstance(port_data, dict):
                raise ValueError(
                    f"Invalid port specification: {port_data}. Must be a dictionary."
                )

            if "container" not in port_data:
                raise ValueError(
                    f"Invalid port specification: {port_data}. Must contain 'container' field."
                )

            container_port = port_data["container"]
            host_port = port_data.get("host")

            if not isinstance(container_port, int):
                raise ValueError(
                    f"Port container must be an integer, got {type(container_port).__name__}"
                )

            if host_port is not None and not isinstance(host_port, int):
                raise ValueError(
                    f"Port host must be an integer or null, got {type(host_port).__name__}"
                )

            default_ports_list.append(
                ExposedPort(host_port=host_port, container_port=container_port)
            )

        # Process default_volumes: strict parsing according to schema
        # Schema format: [{"host": "/path", "container": "/app"}] with "container" required and "host" optional
        default_volumes_data = data.get("default_volumes", [])
        default_volumes_list = []
        for vol_data in default_volumes_data:
            if not isinstance(vol_data, dict):
                raise ValueError(
                    f"Invalid volume specification: {vol_data}. Must be a dictionary."
                )

            if "container" not in vol_data:
                raise ValueError(
                    f"Invalid volume specification: {vol_data}. Must contain 'container' field."
                )

            container_path = vol_data["container"]
            host_path = vol_data.get("host")

            if not isinstance(container_path, str):
                raise ValueError(
                    f"Volume container must be a string, got {type(container_path).__name__}"
                )

            if host_path is not None and not isinstance(host_path, str):
                raise ValueError(
                    f"Volume host must be a string or null, got {type(host_path).__name__}"
                )

            default_volumes_list.append(
                Volume(host_path=host_path, container_path=container_path)
            )

        # Process labels: should be a list of {"key": ..., "value": ...} dicts
        labels_data = data.get("labels", [])
        if not isinstance(labels_data, list):
            raise ValueError(f"labels must be a list, got {type(labels_data).__name__}")
        labels_list = labels_data

        # Process default_contents: strict parsing according to schema
        # Schema format: [{"location": "/path/to/file", "content": "file content"}] with both required
        default_contents_data = data.get("default_contents", [])
        default_contents_list = []
        for content_data in default_contents_data:
            if not isinstance(content_data, dict):
                raise ValueError(
                    f"Invalid default content specification: {content_data}. Must be a dictionary."
                )

            if "location" not in content_data:
                raise ValueError(
                    f"Invalid default content specification: {content_data}. Must contain 'location' field."
                )

            if "content" not in content_data:
                raise ValueError(
                    f"Invalid default content specification: {content_data}. Must contain 'content' field."
                )

            location = content_data["location"]
            content = content_data["content"]

            if not isinstance(location, str):
                raise ValueError(
                    f"Default content location must be a string, got {type(location).__name__}"
                )

            if not isinstance(content, str):
                raise ValueError(
                    f"Default content must be a string, got {type(content).__name__}"
                )

            default_contents_list.append(
                DefaultContent(location=location, content=content)
            )

        # Delegate to create method for further validation
        try:
            template: "Template" = cls.create(
                name=data.get("name", ""),
                type=template_type,
                image=data.get("image"),
                dockerfile=data.get("dockerfile"),
                description=data.get("description"),
                default_env=EnvVariable.from_dict_array(default_env_list),
                default_ports=default_ports_list,
                default_volumes=default_volumes_list,
                default_contents=default_contents_list,
                start_cmd=data.get("start_cmd"),
                healthcheck=Healthcheck.from_dict(data.get("healthcheck")),
                labels=Label.from_dict_array(labels_list),
                args=data.get("args"),
            )
            get_logger(__name__).info(
                f"Successfully imported template '{template.name}' from JSON"
            )
            return template
        except Exception as e:
            get_logger(__name__).error(f"Failed to import template from JSON: {str(e)}")
            raise

    def delete(self) -> None:
        """Deletes the template and associated Docker image if applicable.

        Raises:
            Exception: If the template is associated with existing services.
        """
        get_logger(__name__).info(f"Deleting template '{self.name}'")

        from svs_core.docker.service import Service

        services = Service.objects.filter(template=self)

        if len(services) > 0:
            get_logger(__name__).warning(
                f"Cannot delete template '{self.name}' - has {len(services)} associated services"
            )
            raise Exception(
                f"Cannot delete template {self.name} as it is associated with existing services."
            )

        try:
            if self.type == TemplateType.IMAGE and self.image:
                if DockerImageManager.exists(self.image):
                    get_logger(__name__).debug(
                        f"Removing associated image '{self.image}' for template '{self.name}'"
                    )
                    DockerImageManager.remove(self.image)

            super().delete()
            get_logger(__name__).info(f"Successfully deleted template '{self.name}'")
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to delete template '{self.name}': {str(e)}"
            )
            raise
