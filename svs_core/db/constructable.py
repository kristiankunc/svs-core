from abc import ABC, abstractmethod
from typing import TypeVar, Type, cast

T = TypeVar('T', bound="ConstructableFromORM")


class ConstructableException(Exception):
    pass


class ConstructableFromORM(ABC):
    def __init__(self, *, _orm_check: bool = False) -> None:
        if not _orm_check:
            raise ConstructableException(
                "ConstructableFromORM can only be instantiated from ORM models using the from_orm method.")
        super().__init__()

    @staticmethod
    @abstractmethod
    def from_orm(model: object, **kwargs: object) -> "ConstructableFromORM":
        pass

    @classmethod
    def from_orm_generic(cls: Type[T], model: object, **kwargs: object) -> T:
        return cast(T, cls.from_orm(model, **kwargs))