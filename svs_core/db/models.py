from enum import Enum
from typing import TYPE_CHECKING

from django.db import models

from svs_core.docker.json_properties import (
    DefaultContent,
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.shared.text import indentate, to_goated_time_format

if TYPE_CHECKING:
    from svs_core.docker.service import Service
    from svs_core.docker.template import Template
    from svs_core.shared.git_source import GitSource
    from svs_core.users.user import User


class UserManager(models.Manager["UserModel"]):  # type: ignore[misc]
    """Typed manager for UserModel."""


class TemplateManager(models.Manager["TemplateModel"]):  # type: ignore[misc]
    """Typed manager for TemplateModel."""


class ServiceManager(models.Manager["ServiceModel"]):  # type: ignore[misc]
    """Typed manager for ServiceModel."""


class GitSourceManager(models.Manager["GitSourceModel"]):  # type: ignore[misc]
    """Typed manager for GitSourceModel."""


class BaseModel(models.Model):  # type: ignore[misc]
    """Base model with common fields."""

    id = models.AutoField(primary_key=True)
    """Primary key auto-incrementing integer."""

    created_at = models.DateTimeField(auto_now_add=True)
    """Record creation timestamp."""

    updated_at = models.DateTimeField(auto_now=True)
    """Record last update timestamp."""

    class Meta:  # noqa: D106
        abstract = True


class UserModel(BaseModel):
    """User model."""

    objects = UserManager()
    """Manager for UserModel queries."""

    name = models.CharField(max_length=255, unique=True)
    """Username, tied to the system user's account."""
    password = models.CharField(max_length=255, null=True)
    """Hashed password for authentication."""

    @property
    def proxy_services(self) -> models.QuerySet["Service"]:
        """Get related ServiceModel instances."""
        from svs_core.docker.service import Service

        return Service.objects.filter(user_id=self.id)

    class Meta:  # noqa: D106
        db_table = "users"


class TemplateType(str, Enum):
    """Type of template."""

    IMAGE = "image"  # e.g. nginx:stable, wordpress:latest
    BUILD = "build"  # requires dockerfile/source

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:  # noqa: D102
        return [(key.value, key.name) for key in cls]


class TemplateModel(BaseModel):
    """Template model."""

    name = models.CharField(max_length=255)
    """Name of the template."""
    type = models.CharField(
        max_length=10, choices=TemplateType.choices(), default=TemplateType.IMAGE
    )
    """Type of template (image or build)"""
    image = models.CharField(max_length=255, null=True, blank=True)
    """Docker image name and tag."""
    dockerfile = models.TextField(null=True, blank=True)
    """Dockerfile content for build-type templates."""
    description = models.TextField(null=True, blank=True)
    """Description of the template."""
    start_cmd = models.CharField(max_length=512, null=True, blank=True)
    """Default start command for containers."""
    args = models.JSONField(null=True, blank=True, default=list)
    """Default arguments for the start command."""

    _default_env = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized default environment variables."""
    _default_ports = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized default exposed ports."""
    _default_volumes = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized default volumes."""
    _default_contents = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized default file contents."""
    _healthcheck = models.JSONField(null=True, blank=True, default=dict)
    """JSON-serialized healthcheck configuration."""
    _labels = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized labels."""

    @property
    def default_env(self) -> list[EnvVariable]:
        """Default environment variables (deserialized from JSON)."""
        return EnvVariable.from_dict_array(self._default_env or [])

    @default_env.setter
    def default_env(self, env_vars: list[EnvVariable]) -> None:
        """Set default environment variables (serialized to JSON)."""
        self._default_env = EnvVariable.to_dict_array(env_vars)

    @property
    def default_ports(self) -> list[ExposedPort]:
        """Default exposed ports (deserialized from JSON)."""
        return ExposedPort.from_dict_array(self._default_ports or [])

    @default_ports.setter
    def default_ports(self, ports: list[ExposedPort]) -> None:
        """Set default exposed ports (serialized to JSON)."""
        self._default_ports = ExposedPort.to_dict_array(ports)

    @property
    def default_volumes(self) -> list[Volume]:
        """Default volumes (deserialized from JSON)."""
        return Volume.from_dict_array(self._default_volumes or [])

    @default_volumes.setter
    def default_volumes(self, volumes: list[Volume]) -> None:
        """Set default volumes (serialized to JSON)."""
        self._default_volumes = Volume.to_dict_array(volumes)

    @property
    def default_contents(self) -> list[DefaultContent]:
        """Default file contents (deserialized from JSON)."""
        return DefaultContent.from_dict_array(self._default_contents or [])

    @default_contents.setter
    def default_contents(self, contents: list[DefaultContent]) -> None:
        """Set default file contents (serialized to JSON)."""
        self._default_contents = DefaultContent.to_dict_array(contents)

    @property
    def healthcheck(self) -> Healthcheck | None:
        """Healthcheck configuration (deserialized from JSON)."""
        return (
            Healthcheck.from_dict(self._healthcheck)
            if self._healthcheck is not None
            else None
        )

    @healthcheck.setter
    def healthcheck(self, healthcheck: Healthcheck | None) -> None:
        """Set healthcheck configuration (serialized to JSON)."""
        self._healthcheck = healthcheck.to_dict() if healthcheck is not None else None

    @property
    def labels(self) -> list[Label]:
        """Labels (deserialized from JSON)."""
        return Label.from_dict_array(self._labels or [])

    @labels.setter
    def labels(self, labels: list[Label]) -> None:
        """Set labels (serialized to JSON)."""
        self._labels = Label.to_dict_array(labels)

    class Meta:  # noqa: D106
        db_table = "templates"

    @property
    def proxy_services(self) -> models.QuerySet["Service"]:
        """Get related ServiceModel instances."""
        from svs_core.docker.service import Service

        return Service.objects.filter(template_id=self.id)


class ServiceStatus(str, Enum):
    """Status of a service."""

    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    EXITED = "exited"
    ERROR = "error"

    @classmethod
    def choices(cls) -> list[tuple[str, str]]:  # noqa: D102
        """Return choices for Django model field.

        Note:
            Deprecated in favor of dynamically fetching status from Docker.
        """
        return [(key.value, key.name) for key in cls]

    @classmethod
    def from_str(cls, status_str: str) -> "ServiceStatus":
        """Convert string to ServiceStatus enum."""
        for status in cls:
            if status.value == status_str:
                return status
        raise ValueError(f"Unknown status string: {status_str}")


class ServiceModel(BaseModel):
    """Service model."""

    objects = ServiceManager()
    """Manager for ServiceModel queries."""

    name = models.CharField(max_length=255)
    """Name of the service."""
    container_id = models.CharField(max_length=255, null=True, blank=True)
    """Docker container ID."""
    image = models.CharField(max_length=255, null=True, blank=True)
    """Docker image name and tag."""
    domain = models.CharField(max_length=255, null=True, blank=True)
    """Domain name for the service."""
    command = models.CharField(max_length=512, null=True, blank=True)
    """Command to execute in the container."""
    args = models.JSONField(null=True, blank=True, default=list)
    """Arguments for the command."""

    _env = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized environment variables."""
    _exposed_ports = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized exposed ports."""
    _volumes = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized volumes."""
    _labels = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized labels."""
    _healthcheck = models.JSONField(null=True, blank=True, default=dict)
    """JSON-serialized healthcheck configuration."""
    _networks = models.JSONField(null=True, blank=True, default=list)
    """JSON-serialized networks."""

    template = models.ForeignKey(
        TemplateModel, on_delete=models.CASCADE, related_name="services"
    )
    """Reference to the template this service is based on."""
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="services"
    )
    """Reference to the user that owns this service."""

    @property
    def env(self) -> list[EnvVariable]:
        """Environment variables (deserialized from JSON)."""
        return EnvVariable.from_dict_array(self._env or [])

    @env.setter
    def env(self, env_vars: list[EnvVariable]) -> None:
        """Set environment variables (serialized to JSON)."""
        self._env = EnvVariable.to_dict_array(env_vars)

    @property
    def exposed_ports(self) -> list[ExposedPort]:
        """Exposed ports (deserialized from JSON)."""
        return ExposedPort.from_dict_array(self._exposed_ports or [])

    @exposed_ports.setter
    def exposed_ports(self, ports: list[ExposedPort]) -> None:
        """Set exposed ports (serialized to JSON)."""
        self._exposed_ports = ExposedPort.to_dict_array(ports)

    @property
    def volumes(self) -> list[Volume]:
        """Volumes (deserialized from JSON)."""
        return Volume.from_dict_array(self._volumes or [])

    @volumes.setter
    def volumes(self, volumes: list[Volume]) -> None:
        """Set volumes (serialized to JSON)."""
        self._volumes = Volume.to_dict_array(volumes)

    @property
    def labels(self) -> list[Label]:
        """Labels (deserialized from JSON)."""
        return Label.from_dict_array(self._labels or [])

    @labels.setter
    def labels(self, labels: list[Label]) -> None:
        """Set labels (serialized to JSON)."""
        self._labels = Label.to_dict_array(labels)

    @property
    def healthcheck(self) -> Healthcheck | None:
        """Healthcheck configuration (deserialized from JSON)."""
        return (
            Healthcheck.from_dict(self._healthcheck)
            if self._healthcheck is not None
            else None
        )

    @healthcheck.setter
    def healthcheck(self, healthcheck: Healthcheck | None) -> None:
        """Set healthcheck configuration (serialized to JSON)."""
        self._healthcheck = healthcheck.to_dict() if healthcheck is not None else None

    @property
    def networks(self) -> list[str]:
        """Networks the service is connected to."""
        return self._networks.split(",") if self._networks else []

    @networks.setter
    def networks(self, networks: list[str] | None) -> None:
        """Set networks the service is connected to."""
        self._networks = ",".join(networks) if networks else None

    class Meta:  # noqa: D106
        db_table = "services"

    @property
    def proxy_template(self) -> models.QuerySet["Template"]:
        """Get related TemplateModel instance."""
        from svs_core.docker.template import Template

        return Template.objects.filter(id=self.template_id)

    @property
    def proxy_user(self) -> models.QuerySet["User"]:
        """Get related UserModel instance."""
        from svs_core.users.user import User

        return User.objects.filter(id=self.user_id)

    @property
    def proxy_git_sources(self) -> models.QuerySet["GitSource"]:
        """Get related GitSourceModel instances."""
        from svs_core.shared.git_source import GitSource

        return GitSource.objects.filter(service_id=self.id)


class GitSourceModel(BaseModel):
    """Git Source model."""

    objects = GitSourceManager()
    """Manager for GitSourceModel queries."""

    repository_url = models.CharField(max_length=512)
    """URL of the git repository."""
    branch = models.CharField(max_length=255, null=True, blank=True)
    """Branch to checkout."""
    destination_path = models.CharField(max_length=512, null=True, blank=True)
    """Destination path inside the service volume on host filesystem."""
    service = models.ForeignKey(
        ServiceModel, on_delete=models.CASCADE, related_name="git_sources"
    )
    is_temporary = models.BooleanField(default=False)
    """Indicates if the git source is temporary (for BUILD services)."""

    class Meta:  # noqa: D106
        db_table = "git_sources"

    @property
    def proxy_service(self) -> models.QuerySet["Service"]:
        """Get related ServiceModel instance."""
        from svs_core.docker.service import Service

        return Service.objects.filter(id=self.service_id)


def miscelanous_str_injector(obj: BaseModel, indent: int = 1) -> str:
    """Generate miscelanous information string for a model instance.

    Args:
        obj (BaseModel): The model instance.
        indent (int): The indentation level in spaces * 4. Default is 1.

    Returns:
        str: Formatted miscelanous information string.
    """
    return indentate(
        f"""ID: {obj.id}
Created At: {to_goated_time_format(obj.created_at)}
Last Updated: {to_goated_time_format(obj.updated_at)}""",
        level=indent,
    )
