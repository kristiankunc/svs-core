from enum import Enum

from django.db import models

from svs_core.docker.json_properties import (
    DefaultContent,
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)


class UserManager(models.Manager["UserModel"]):  # type: ignore[misc]
    """Typed manager for UserModel."""


class TemplateManager(models.Manager["TemplateModel"]):  # type: ignore[misc]
    """Typed manager for TemplateModel."""


class ServiceManager(models.Manager["ServiceModel"]):  # type: ignore[misc]
    """Typed manager for ServiceModel."""


class BaseModel(models.Model):  # type: ignore[misc]
    """Base model with common fields."""

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:  # noqa: D106
        abstract = True


class UserModel(BaseModel):
    """User model."""

    objects = UserManager()

    name = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255, null=True)

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

    objects = TemplateManager()

    name = models.CharField(max_length=255)
    type = models.CharField(
        max_length=10, choices=TemplateType.choices(), default=TemplateType.IMAGE
    )
    image = models.CharField(max_length=255, null=True, blank=True)
    dockerfile = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    start_cmd = models.CharField(max_length=512, null=True, blank=True)
    args = models.JSONField(null=True, blank=True, default=list)

    _default_env = models.JSONField(null=True, blank=True, default=list)
    _default_ports = models.JSONField(null=True, blank=True, default=list)
    _default_volumes = models.JSONField(null=True, blank=True, default=list)
    _default_contents = models.JSONField(null=True, blank=True, default=list)
    _healthcheck = models.JSONField(null=True, blank=True, default=dict)
    _labels = models.JSONField(null=True, blank=True, default=list)

    @property
    def default_env(self) -> list[EnvVariable]:  # noqa: D102
        return EnvVariable.from_dict_array(self._default_env or [])

    @default_env.setter
    def default_env(self, env_vars: list[EnvVariable]) -> None:  # noqa: D102
        self._default_env = EnvVariable.to_dict_array(env_vars)

    @property
    def default_ports(self) -> list[ExposedPort]:  # noqa: D102
        return ExposedPort.from_dict_array(self._default_ports or [])

    @default_ports.setter
    def default_ports(self, ports: list[ExposedPort]) -> None:  # noqa: D102
        self._default_ports = ExposedPort.to_dict_array(ports)

    @property
    def default_volumes(self) -> list[Volume]:  # noqa: D102
        return Volume.from_dict_array(self._default_volumes or [])

    @default_volumes.setter
    def default_volumes(self, volumes: list[Volume]) -> None:
        self._default_volumes = Volume.to_dict_array(volumes)

    @property
    def default_contents(self) -> list[DefaultContent]:  # noqa: D102
        return DefaultContent.from_dict_array(self._default_contents or [])

    @default_contents.setter
    def default_contents(self, contents: list[DefaultContent]) -> None:  # noqa: D102
        self._default_contents = DefaultContent.to_dict_array(contents)

    @property
    def healthcheck(self) -> Healthcheck | None:  # noqa: D102
        return (
            Healthcheck.from_dict(self._healthcheck)
            if self._healthcheck is not None
            else None
        )

    @healthcheck.setter
    def healthcheck(self, healthcheck: Healthcheck | None) -> None:  # noqa: D102
        self._healthcheck = healthcheck.to_dict() if healthcheck is not None else None

    @property
    def labels(self) -> list[Label]:  # noqa: D102
        return Label.from_dict_array(self._labels or [])

    @labels.setter
    def labels(self, labels: list[Label]) -> None:  # noqa: D102
        self._labels = Label.to_dict_array(labels)

    class Meta:  # noqa: D106
        db_table = "templates"


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

    name = models.CharField(max_length=255)
    container_id = models.CharField(max_length=255, null=True, blank=True)
    image = models.CharField(max_length=255, null=True, blank=True)
    domain = models.CharField(max_length=255, null=True, blank=True)
    command = models.CharField(max_length=512, null=True, blank=True)
    args = models.JSONField(null=True, blank=True, default=list)

    _env = models.JSONField(null=True, blank=True, default=list)
    _exposed_ports = models.JSONField(null=True, blank=True, default=list)
    _volumes = models.JSONField(null=True, blank=True, default=list)
    _labels = models.JSONField(null=True, blank=True, default=list)
    _healthcheck = models.JSONField(null=True, blank=True, default=dict)
    _networks = models.JSONField(null=True, blank=True, default=list)

    template = models.ForeignKey(
        TemplateModel, on_delete=models.CASCADE, related_name="services"
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="services"
    )

    @property
    def env(self) -> list[EnvVariable]:  # noqa: D102
        return EnvVariable.from_dict_array(self._env or [])

    @env.setter
    def env(self, env_vars: list[EnvVariable]) -> None:  # noqa: D102
        self._env = EnvVariable.to_dict_array(env_vars)

    @property
    def exposed_ports(self) -> list[ExposedPort]:  # noqa: D102
        return ExposedPort.from_dict_array(self._exposed_ports or [])

    @exposed_ports.setter
    def exposed_ports(self, ports: list[ExposedPort]) -> None:  # noqa: D102
        self._exposed_ports = ExposedPort.to_dict_array(ports)

    @property
    def volumes(self) -> list[Volume]:  # noqa: D102
        return Volume.from_dict_array(self._volumes or [])

    @volumes.setter
    def volumes(self, volumes: list[Volume]) -> None:  # noqa: D102
        self._volumes = Volume.to_dict_array(volumes)

    @property
    def labels(self) -> list[Label]:  # noqa: D102
        return Label.from_dict_array(self._labels or [])

    @labels.setter
    def labels(self, labels: list[Label]) -> None:  # noqa: D102
        self._labels = Label.to_dict_array(labels)

    @property
    def healthcheck(self) -> Healthcheck | None:  # noqa: D102
        return (
            Healthcheck.from_dict(self._healthcheck)
            if self._healthcheck is not None
            else None
        )

    @healthcheck.setter
    def healthcheck(self, healthcheck: Healthcheck | None) -> None:  # noqa: D102
        self._healthcheck = healthcheck.to_dict() if healthcheck is not None else None

    @property
    def networks(self) -> list[str]:  # noqa: D102
        return self._networks.split(",") if self._networks else []

    @networks.setter
    def networks(self, networks: list[str] | None) -> None:  # noqa: D102
        self._networks = ",".join(networks) if networks else None

    class Meta:  # noqa: D106
        db_table = "services"
