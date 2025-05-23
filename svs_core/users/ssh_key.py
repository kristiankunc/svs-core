import re
from typing import TYPE_CHECKING
from svs_core.db.constructable import ConstructableFromORM
from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.event_adapters.db import DBAdapter
from typing import cast
from svs_core.db.models import SSHKeyModel

if TYPE_CHECKING:
    from svs_core.users.user import User


class SSHKey(ConstructableFromORM):
    """
    Represents an SSH key associated with a user.

    Attributes:
        id (int): The unique identifier of the SSH key.
        name (str): The name of the SSH key.
        content (str): The content of the SSH key.
        user (User): The user associated with the SSH key.
    """

    def __init__(
        self,
        id: int,
        name: str,
        content: str,
        user: "User",
        *,
        _orm_check: bool = False,
    ):
        super().__init__(_orm_check=_orm_check)

        self.id = id
        self.name = name
        self.content = content
        self.user = user

    @staticmethod
    def from_orm(model: object, **kwargs: object) -> "SSHKey":
        model = cast(SSHKeyModel, model)
        return SSHKey(
            id=model.id,
            name=model.name,
            content=model.content,
            user=cast(User, kwargs.get("user")),
            _orm_check=True,
        )

    @staticmethod
    def is_valid(name: str, content: str) -> bool:
        """Check if the SSH key is valid.
        The name must be between 1 and 32 characters long.
        The content must be a valid SSH key format.

        Args:
            name (str): The name of the SSH key.
            content (str): The content of the SSH key.
        Returns:
            bool: True if the SSH key is valid, False otherwise.
        """
        if not name or len(name) > 32:
            return False

        if len(content) > 4096:
            return False

        ssh_key_pattern = r"^(ssh-(rsa|dss|ed25519|ecdsa) AAAA[0-9A-Za-z+/]+[=]{0,3} .+)|(ecdsa-sha2-nistp[0-9]+ AAAA[0-9A-Za-z+/]+[=]{0,3} .+)$"
        match = re.match(ssh_key_pattern, content)

        return bool(match)

    def delete(self) -> None:
        """Delete the SSH key from the database and remove it from the user."""
        self.user.ssh_keys.remove(self)

        SideEffectAdapter.dispatch_delete_ssh_key(self.user, self)
        DBAdapter.delete_ssh_key(self.user, self)
        self.user.ssh_keys.remove(self)

        # TODO: destruct
