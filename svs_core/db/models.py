from enum import Enum

from django.db import models


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
    default_env = models.JSONField(null=True, blank=True, default=dict)
    default_ports = models.JSONField(null=True, blank=True, default=list)
    default_volumes = models.JSONField(null=True, blank=True, default=list)
    start_cmd = models.CharField(max_length=512, null=True, blank=True)
    healthcheck = models.JSONField(null=True, blank=True, default=dict)
    labels = models.JSONField(null=True, blank=True, default=dict)
    args = models.JSONField(null=True, blank=True, default=list)

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
    env = models.JSONField(null=True, blank=True, default=dict)
    exposed_ports = models.JSONField(null=True, blank=True, default=list)
    volumes = models.JSONField(null=True, blank=True, default=list)
    command = models.CharField(max_length=512, null=True, blank=True)
    labels = models.JSONField(null=True, blank=True, default=dict)
    args = models.JSONField(null=True, blank=True, default=list)
    healthcheck = models.JSONField(null=True, blank=True, default=dict)
    networks = models.JSONField(null=True, blank=True, default=list)
    exit_code = models.IntegerField(null=True, blank=True)
    template = models.ForeignKey(
        TemplateModel, on_delete=models.CASCADE, related_name="services"
    )
    user = models.ForeignKey(
        UserModel, on_delete=models.CASCADE, related_name="services"
    )

    class Meta:  # noqa: D106
        db_table = "services"
