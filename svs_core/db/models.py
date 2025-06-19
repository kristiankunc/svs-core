from abc import ABC
from datetime import datetime
from typing import Any, Optional, Type, TypeVar
from weakref import WeakSet

from tortoise import BaseDBAsyncClient, fields
from tortoise.models import Model
from tortoise.signals import post_save

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
        models = await cls._model_cls.filter(**{key: value})
        if len(models) != 1:
            return None
        model = models[0]
        if not isinstance(model, BaseModel):
            raise TypeError("Model is not an instance of BaseModel")
        return cls(model=model, **model.__dict__)


class BaseModel(Model):
    id = fields.IntField(pk=True, null=False)
    created_at = fields.DatetimeField(auto_now_add=True, null=False)
    updated_at = fields.DatetimeField(auto_now=True, null=False)

    class Meta:
        abstract = True


class UserModel(BaseModel):
    name = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, unique=True, null=False)
    password = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "users"


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
