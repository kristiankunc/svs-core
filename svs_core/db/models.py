import os
from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Type, TypeVar
from weakref import WeakSet

from tortoise import BaseDBAsyncClient, fields
from tortoise.models import Model
from tortoise.signals import post_save

from svs_core.shared.logger import get_logger

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    get_logger(__name__).error("DATABASE_URL environment variable is not set.")
    exit(1)


TORTOISE_ORM = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["aerich.models", "svs_core.db.models"],
            "default_connection": "default",
        },
    },
}

T = TypeVar("T", bound="OrmBase")


class OrmBase(ABC):
    """Base class for objects tied to an ORM model."""

    _model_cls: Type["BaseModel"] = None  # type: ignore[assignment]
    _instances: WeakSet["OrmBase"] = WeakSet()

    def __init__(self, model: "BaseModel"):
        self._model = model
        self._instances.add(self)

    @classmethod
    def get_instances(cls) -> list["OrmBase"]:
        return list(cls._instances)

    @property
    def id(self) -> int:
        return self._model.id

    @property
    def created_at(self) -> datetime:
        return self._model.created_at

    @property
    def updated_at(self) -> datetime:
        return self._model.updated_at

    @classmethod
    async def _get(cls: Type[T], key: str, value: Any) -> Optional[T]:
        """
        Retrieves an instance by a specific key and value.

        Args:
            key (str): The field name to filter by.
            value (Any): The value to match against the field.
        Returns:
            Optional[T]: An instance of the class if found, otherwise None.
        """
        models = await cls._model_cls.filter(**{key: value})
        if len(models) != 1:
            return None
        model = models[0]
        if not isinstance(model, BaseModel):
            raise TypeError("Model is not an instance of BaseModel")

        return cls(model=model)

    @classmethod
    async def _exists(cls: Type[T], key: str, value: Any) -> bool:
        """
        Checks if an instance with the given key and value exists.
        Args:
            key (str): The field name to check.
            value (Any): The value to check for.
        Returns:
            bool: True if an instance exists, False otherwise.
        """

        models = await cls._model_cls.filter(**{key: value})
        return len(models) > 0

    @classmethod
    async def get_all(cls: Type[T]) -> list[T]:
        """
        Retrieves all instances of the class, with all related fields prefetched.

        Returns:
            list[T]: A list of instances of the class.
        """
        related_fields = []
        for field_name, field in cls._model_cls._meta.fields_map.items():
            if isinstance(
                field,
                (
                    fields.relational.ForeignKeyFieldInstance,
                    fields.relational.BackwardFKRelation,
                ),
            ):
                related_fields.append(field_name)

        query = cls._model_cls.all().prefetch_related(*related_fields)
        models = await query
        return [cls(model=model) for model in models]

    @classmethod
    async def get_by_id(cls: Type[T], id: int) -> Optional[T]:
        """
        Retrieves an instance by its ID, with all related fields prefetched.

        Args:
            id (int): The ID of the instance to retrieve.
        Returns:
            Optional[T]: An instance of the class if found, otherwise None.
        """

        related_fields = []
        for field_name, field in cls._model_cls._meta.fields_map.items():
            if isinstance(
                field,
                (
                    fields.relational.ForeignKeyFieldInstance,
                    fields.relational.BackwardFKRelation,
                ),
            ):
                related_fields.append(field_name)

        query = cls._model_cls.filter(id=id)
        if related_fields:
            query = query.prefetch_related(*related_fields)

        models = await query
        if not models:
            return None
        model = models[0]
        return cls(model=model)

    def __str__(self) -> str:
        return str(self.__dict__)


class BaseModel(Model):
    id = fields.IntField(primary_key=True, null=False)
    created_at = fields.DatetimeField(auto_now_add=True, null=False)
    updated_at = fields.DatetimeField(auto_now=True, null=False)

    class Meta:
        abstract = True


class UserModel(BaseModel):
    name = fields.CharField(max_length=255, null=False, unique=True)
    password = fields.CharField(max_length=255, null=True)

    services: fields.ReverseRelation["ServiceModel"]

    class Meta:
        table = "users"


class TemplateType(str, Enum):
    IMAGE = "image"  # e.g. nginx:stable, wordpress:latest
    BUILD = "build"  # requires dockerfile/source


class TemplateModel(BaseModel):
    name = fields.CharField(max_length=255, null=False)

    # IMAGE vs BUILD
    type = fields.CharEnumField(TemplateType, default=TemplateType.IMAGE)

    # For IMAGE templates
    image = fields.CharField(max_length=255, null=True, default=None)

    # For BUILD templates
    dockerfile = fields.TextField(null=True, default=None)

    description = fields.TextField(null=True)

    # Defaults applied when creating services
    default_env: dict[str, str] = fields.JSONField(null=True, default=dict)
    default_ports: list[dict[str, Any]] = fields.JSONField(
        null=True, default=list
    )  # [{ "container": 80, "host": None }]
    default_volumes: list[dict[str, Any]] = fields.JSONField(
        null=True, default=list
    )  # [{ "container": "/usr/share/nginx/html", "host": None }]
    start_cmd = fields.CharField(max_length=512, null=True, default=None)
    healthcheck: dict[str, Any] = fields.JSONField(null=True, default=dict)
    labels: dict[str, str] = fields.JSONField(null=True, default=dict)
    args: dict[str, str] = fields.JSONField(null=True, default=dict)

    services: fields.ReverseRelation["ServiceModel"]

    class Meta:
        table = "templates"


class ServiceModel(BaseModel):
    name = fields.CharField(max_length=255, null=False)

    # Docker runtime tracking
    container_id = fields.CharField(max_length=255, null=True, default=None)
    image = fields.CharField(
        max_length=255, null=True, default=None
    )  # actual image used
    domain = fields.CharField(max_length=255, null=True, default=None)

    # Resolved runtime config
    env: dict[str, str] = fields.JSONField(null=True, default=dict)
    ports: list[dict[str, Any]] = fields.JSONField(null=True, default=list)
    volumes: list[dict[str, Any]] = fields.JSONField(null=True, default=list)
    command = fields.CharField(max_length=512, null=True, default=None)
    labels: dict[str, str] = fields.JSONField(null=True, default=dict)
    args: dict[str, str] = fields.JSONField(null=True, default=dict)
    healthcheck: dict[str, Any] = fields.JSONField(null=True, default=dict)
    networks: list[str] = fields.JSONField(null=True, default=list)

    # State
    status = fields.CharField(max_length=64, null=True, default="created")
    exit_code = fields.IntField(null=True, default=None)

    # Relations
    template: fields.ForeignKeyRelation["TemplateModel"] = fields.ForeignKeyField(
        "models.TemplateModel", related_name="services", to_field="id", null=False
    )
    user: fields.ForeignKeyRelation["UserModel"] = fields.ForeignKeyField(
        "models.UserModel", related_name="services", to_field="id", null=False
    )

    class Meta:
        table = "services"


@post_save(BaseModel)
async def signal_post_save(
    sender: type[BaseModel],
    instance: BaseModel,
    created: bool,
    using_db: BaseDBAsyncClient | None,
    update_fields: list[str],
) -> None:
    for subclass in OrmBase.__subclasses__():
        if subclass._model_cls is sender:
            for obj in subclass.get_instances():
                if obj._model.id == instance.id:
                    obj._model = instance
                    obj._model = instance
