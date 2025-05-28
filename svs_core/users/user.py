from datetime import datetime
from typing import cast

from svs_core.db.constructable import ConstructableFromORM
from svs_core.db.models import UserModel
from svs_core.docker.network import DockerNetworkManager


class User(ConstructableFromORM):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        created_at (datetime): The timestamp when the user was created.
        updated_at (datetime): The timestamp when the user was last updated.
        name (str): The name of the user.

    """

    def __init__(
        self,
        id: int,
        created_at: datetime,
        updated_at: datetime,
        name: str,
        *,
        _orm_check: bool = False,
    ):
        super().__init__(id, created_at, updated_at, _orm_check=_orm_check)
        self.name = name

    @staticmethod
    def from_orm(model: object, **kwargs: object) -> "User":
        model = cast(UserModel, model)

        user = User(
            id=model.id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            name=model.name,
            _orm_check=True,
        )
        return user

    def delete_self(self) -> None:
        """Deletes the user"""

        from svs_core.db.client import DBClient

        DBClient.delete_user(self.id)
        DockerNetworkManager.delete_network(self.name)

        ## TODO: destruct properly
