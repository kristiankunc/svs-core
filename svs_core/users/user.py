from typing import cast
from svs_core.db.constructable import ConstructableFromORM
from svs_core.db.models import UserModel


class User(ConstructableFromORM):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier of the user.
        name (str): The name of the user.
        ssh_keys (list[SSHKey]): The list of SSH keys associated with the user.
    """

    def __init__(
        self,
        id: int,
        name: str,
        *,
        _orm_check: bool = False,
    ):
        super().__init__(_orm_check=_orm_check)
        self.id = id
        self.name = name

    @staticmethod
    def from_orm(model: object, **kwargs: object) -> "User":
        model = cast(UserModel, model)

        user = User(
            id=model.id,
            name=model.name,
            _orm_check=True,
        )
        return user

    def delete_self(self) -> None:
        """Deletes the user"""

        from svs_core.db.client import DBClient

        DBClient.delete_user(self.id)

        ## TODO: destruct properly
