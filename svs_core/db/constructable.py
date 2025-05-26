from abc import ABC, abstractmethod
from typing import Type, TypeVar, cast

T = TypeVar("T", bound="ConstructableFromORM")


class ConstructableFromORM(ABC):
    """
    Abstract base class for models that can be constructed from ORM models.
    It serves as a base class for any class that relates directly to an ORM model.
    """

    def __init__(self, *, _orm_check: bool = False) -> None:
        if not _orm_check:
            raise ValueError("This class can only be instantiated from ORM models.")
        super().__init__()

    @staticmethod
    @abstractmethod
    def from_orm(model: object, **kwargs: object) -> "ConstructableFromORM":
        pass

    @classmethod
    def from_orm_generic(cls: Type[T], model: object, **kwargs: object) -> T:
        return cast(T, cls.from_orm(model, **kwargs))
