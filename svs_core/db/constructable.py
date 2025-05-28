from abc import ABC, abstractmethod
from datetime import datetime
from typing import Type, TypeVar, cast

T = TypeVar("T", bound="ConstructableFromORM")


class ConstructableFromORM(ABC):
    """
    Abstract base class for models that can be constructed from ORM models.
    It serves as a base class for any class that relates directly to an ORM model.

    Attributes:
        id (int): The unique identifier for the model.
        created_at (datetime): The timestamp when the object was created.
        updated_at (datetime): The timestamp when the object was last updated.

    """

    def __init__(
        self,
        id: int,
        created_at: datetime,
        updated_at: datetime,
        *,
        _orm_check: bool = False,
    ) -> None:
        if not _orm_check:
            raise ValueError("This class can only be instantiated from ORM models.")
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        super().__init__()

    @staticmethod
    @abstractmethod
    def from_orm(model: object, **kwargs: object) -> "ConstructableFromORM":
        """
        Create an instance of the class from an ORM model.
        Args:
            model (object): The ORM model instance to construct from.
            **kwargs: Additional keyword arguments for customization.
        Returns:
            ConstructableFromORM: An instance of the class constructed from the ORM model.
        """

        pass

    @classmethod
    def from_orm_generic(cls: Type[T], model: object, **kwargs: object) -> T:
        """
        Create an instance of the class from an ORM model using a generic type.
        Args:
            cls (Type[T]): The class type to construct.
            model (object): The ORM model instance to construct from.
            **kwargs: Additional keyword arguments for customization.
        Returns:
            T: An instance of the class constructed from the ORM model.
        """

        return cast(T, cls.from_orm(model, **kwargs))
