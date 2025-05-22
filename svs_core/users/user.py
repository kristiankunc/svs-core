import re
from typing import cast, TYPE_CHECKING
from svs_core.db.constructable import ConstructableFromORM
from svs_core.shared.exceptions import UserAlreadyExistsException
from svs_core.users.manager import UserManager
from svs_core.db.models import UserModel
from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.event_adapters.db import DBAdapter

if TYPE_CHECKING:
    from svs_core.users.ssh_key import SSHKey


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
        ssh_keys: list["SSHKey"] = [],
        *,
        _orm_check: bool = False,
    ):
        super().__init__(_orm_check=_orm_check)
        self.id = id
        self.name = name
        self.ssh_keys = ssh_keys

    @staticmethod
    def from_orm(model: object, **kwargs: object) -> "User":
        model = cast(UserModel, model)

        user = User(
            id=model.id,
            name=model.name,
            ssh_keys=[],
            _orm_check=True,
        )
        user.ssh_keys = [SSHKey.from_orm(k, user=user) for k in model.ssh_keys]
        return user

    @staticmethod
    def is_username_valid(username: str) -> bool:
        """Checks if the username is valid for linux systems."

        Args:
            username (str): The username to check.

        Returns:
            bool: validity of the username.
        """

        if not 1 <= len(username) <= 32:
            return False

        if not re.match(r"^[a-z_][a-z0-9_-]*[$]?$", username):
            return False

        if username.endswith("-"):
            return False

        return True

    @staticmethod
    def create(username: str) -> "User":
        """Creates a new user in the system and database.
        Args:
            username (str): The username to create.

        Returns:
            User: The created user object.

        Raises:
            ValueError: If the username is invalid.
            UserAlreadyExistsException: If the user already exists in the system or database.
        """

        from svs_core.event_adapters.db import DBAdapter

        if not User.is_username_valid(username):
            raise ValueError(f"Invalid username: {username}")

        if UserManager.name_exists_in_system(username) or UserManager.name_exists_in_db(
            username
        ):
            raise UserAlreadyExistsException(
                f"User {username} already exists in system or database."
            )

        SideEffectAdapter.dispatch_create_user(username)
        return DBAdapter.create_user(username)

    def delete(self) -> None:
        """Deletes the user from the system and database."""

        SideEffectAdapter.dispatch_delete_user(self)
        DBAdapter.delete_user(self)

        # TODO: destroy self or sum shit

    def add_ssh_key(self, key_name: str, key_content: str) -> "SSHKey":
        """Adds an SSH key to the user.

        Args:
            key_name (str): The name of the SSH key.
            key_content (str): The content of the SSH key.

        Returns:
            SSHKey: The added SSH key object.

        Raises:
            ValueError: If the SSH key is invalid.
        """

        if not SSHKey.is_valid(key_name, key_content):
            raise ValueError("Invalid SSH key data")

        SideEffectAdapter.dispatch_add_ssh_key(self, key_name, key_content)

        ssh_key = DBAdapter.add_ssh_key(self, key_name, key_content)
        self.ssh_keys.append(ssh_key)

        return ssh_key
