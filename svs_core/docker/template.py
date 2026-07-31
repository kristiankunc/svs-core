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
from svs_core.shared.exceptions import TemplateException, ValidationException
from svs_core.shared.logger import get_logger
from svs_core.shared.text import indentate, to_goated_time_format


class Template(TemplateModel):
    """Template class representing a Docker template in the system."""

    class Meta:  # noqa: D106
        proxy = True

    def __str__(self) -> str:
        dockerfile_head = self.dockerfile.splitlines()[:5] if self.dockerfile else []

        return (
            f"name={self.name}\n"
            f"id={self.id}\n"
            f"type={self.type}\n"
            f"image={self.image}\n"
            f"dockerfile_head={dockerfile_head}\n"
            f"description={self.description}\n"
            f"docs_url={self.docs_url}\n"
            f"default_env={[var.__str__() for var in self.default_env]}\n"
            f"default_ports={[port.__str__() for port in self.default_ports]}\n"
            f"default_volumes={[vol.__str__() for vol in self.default_volumes]}\n"
            f"default_contents={[content.__str__() for content in self.default_contents]}\n"
            f"start_cmd={self.start_cmd}\n"
            f"healthcheck={self.healthcheck}\n"
            f"labels={[label.__str__() for label in self.labels]}\n"
            f"args={self.args}"
        )

    def pprint(self, indent: int = 0) -> str:
        """Pretty-print the template details.

        Args:
            indent (int): The indentation level for formatting.

        Returns:
            str: The pretty-printed template details.
        """
        from svs_core.docker.service import Service

        services = Service.objects.filter(template=self)

        # Handle type as either string or enum
        type_value = self.type.value if hasattr(self.type, "value") else self.type
        type_display = (
            self.type if self.type == TemplateType.BUILD else TemplateType.IMAGE
        )

        return indentate(
            f"""Template: {self.name}
Type: {type_value}
Description: {self.description if self.description else 'None'}
Image: {self.image if type_display == TemplateType.IMAGE else 'Built on-demand (Dockerfile)'}
Documentation: {self.docs_url if self.docs_url else 'None'}

Default Environment Variables:
    {'\n    '.join([f'{var.key}={var.value}' for var in self.default_env]) if self.default_env else 'None'}

Default Ports (Host -> Container):
    {'\n    '.join([f'{port.host_port} -> {port.container_port}' for port in self.default_ports]) if self.default_ports else 'None'}

Default Volumes (Host -> Container):
    {'\n    '.join([f'{vol.host_path} -> {vol.container_path}' for vol in self.default_volumes]) if self.default_volumes else 'None'}

Default Contents:
    {'\n    '.join([f'{content.location}: {len(content.content)} bytes' for content in self.default_contents]) if self.default_contents else 'None'}

Services Using This Template ({len(services)}):
    {'\n    '.join([f"{service.name} (ID: {service.id})" for service in services]) if services else 'None'}

Miscellaneous:
    ID: {self.id}
    Created At: {to_goated_time_format(self.created_at)}
    Last Updated: {to_goated_time_format(self.updated_at)}""",
            level=indent,
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
        docs_url: str | None = None,
    ) -> Template:
        """Creates a new template with all supported attributes.

        Args:
            name (str): The name of the template.
            type (TemplateType): The type of the template (image or build). Defaults to TemplateType.IMAGE.
            image (str | None): The Docker image name (if type is image). Defaults to None.
            dockerfile (str | None): The Dockerfile content (if type is build). Defaults to None.
            description (str | None): A description of the template. Defaults to None.
            default_env (list[EnvVariable] | None): Default environment variables. Defaults to None.
            default_ports (list[ExposedPort] | None): Default exposed ports. Defaults to None.
            default_volumes (list[Volume] | None): Default volume bindings. Defaults to None.
            default_contents (list[DefaultContent] | None): Default file contents to create in the container. Defaults to None.
            start_cmd (str | None): The default start command. Defaults to None.
            healthcheck (Healthcheck | None): The healthcheck configuration. Defaults to None.
            labels (list[Label] | None): Default Docker labels. Defaults to None.
            args (list[str] | None): Default arguments for the container. Defaults to None.
            docs_url (str | None): URL to documentation for this template. Defaults to None.

        Returns:
            Template: A new Template instance.

        Raises:
            ValidationException: If any of the provided values are invalid.
        """

        # Validate name (business rule)
        if not name:
            raise ValidationException("Template name cannot be empty")

        # Validate type-specific requirements (business rules)
        if type == TemplateType.IMAGE:
            if not image:
                raise ValidationException("Image type templates must specify an image")
        elif type == TemplateType.BUILD:
            if not dockerfile:
                raise ValidationException(
                    "Build type templates must specify a dockerfile"
                )

        # Validate healthcheck test (business rule)
        if healthcheck is not None and len(healthcheck.test) == 0:
            raise ValidationException("Healthcheck must contain a 'test' field")

        # All type/value validation delegated to Pydantic models

        get_logger(__name__).info(f"Creating template '{name}' of type '{type}'")
        get_logger(__name__).debug(
            f"Template details: image={image}, dockerfile={'set' if dockerfile else 'None'}, "
            f"description={description}, default_env={default_env}, default_ports={default_ports}, "
            f"default_volumes={default_volumes}, default_contents={default_contents}, start_cmd={start_cmd}, healthcheck={healthcheck}, "
            f"labels={labels}, args={args}, docs_url={docs_url}"
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
            docs_url=docs_url,
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
            TemplateException: If the data is invalid or missing required fields.
        """
        get_logger(__name__).info(
            f"Importing template from JSON: {data.get('name', 'unnamed')}"
        )

        if not isinstance(data, dict):
            raise TemplateException(
                f"Template import data must be a dictionary, got {type(data)}"
            )
        if "name" not in data:
            raise TemplateException("Template import data must contain a 'name' field")

        # Validate and parse template type
        template_type = data.get("type", "image")
        try:
            template_type = TemplateType(template_type)
        except ValueError:
            valid_types = [t.value for t in TemplateType]
            raise TemplateException(
                f"Invalid template type: {template_type}. Must be one of: {valid_types}"
            )

        # Validate type-specific required fields
        if template_type == TemplateType.IMAGE and "image" not in data:
            raise TemplateException(
                "Image type templates must specify an 'image' field in import data"
            )
        if template_type == TemplateType.BUILD and "dockerfile" not in data:
            raise TemplateException(
                "Build type templates must specify a 'dockerfile' field in import data"
            )

        # Parse nested structures — Pydantic validates types/values
        default_env = [
            EnvVariable(key=e["key"], value=e["value"])
            for e in data.get("default_env") or []
        ]
        default_ports = [
            ExposedPort(host_port=p.get("host"), container_port=p["container"])
            for p in data.get("default_ports") or []
        ]
        default_volumes = [
            Volume(host_path=v.get("host"), container_path=v["container"])
            for v in data.get("default_volumes") or []
        ]
        default_contents = [
            DefaultContent(location=c["location"], content=c["content"])
            for c in data.get("default_contents") or []
        ]
        labels = [
            Label(key=l["key"], value=l["value"]) for l in data.get("labels") or []
        ]

        # Delegate to create — Pydantic + business rule validation applies
        try:
            template: "Template" = cls.create(
                name=data["name"],
                type=template_type,
                image=data.get("image"),
                dockerfile=data.get("dockerfile"),
                description=data.get("description"),
                default_env=default_env,
                default_ports=default_ports,
                default_volumes=default_volumes,
                default_contents=default_contents,
                start_cmd=data.get("start_cmd"),
                healthcheck=Healthcheck.from_dict(data.get("healthcheck")),
                labels=labels,
                args=data.get("args"),
                docs_url=data.get("docs_url"),
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
            InvalidOperationException: If the template is associated with existing services.
        """
        get_logger(__name__).info(f"Deleting template '{self.name}'")

        from svs_core.docker.service import Service
        from svs_core.shared.exceptions import InvalidOperationException

        services = Service.objects.filter(template=self)

        if len(services) > 0:
            get_logger(__name__).warning(
                f"Cannot delete template '{self.name}' - has {len(services)} associated services"
            )
            raise InvalidOperationException(
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
