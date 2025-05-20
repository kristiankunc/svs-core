import re

from svs_core.db.constructable import ConstructableFromORM
from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.event_adapters.db import DBAdapter
from svs_core.users.ssh_key import SSHKey
from typing import cast
from svs_core.db.models import UserModel


class User(ConstructableFromORM):
    def __init__(self,
                 id: int,
                 name: str,
                 ssh_keys: list["SSHKey"] = [],
                 *,
                 _orm_check: bool = False):
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
        user.ssh_keys = [
            SSHKey.from_orm(k, user=user)
            for k in model.ssh_keys
        ]
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

        if not re.match(r'^[a-z_][a-z0-9_-]*[$]?$', username):
            return False

        if username.endswith('-'):
            return False

        return True
    
    def delete(self) -> None:
        SideEffectAdapter.dispatch_delete_user(self)
        DBAdapter.delete_user(self)

        # TODO: destroy self or sum shit

    def add_ssh_key(self, key_name: str, key_content: str) -> "SSHKey":
        if not SSHKey.is_valid(key_name, key_content): 
            raise ValueError("Invalid SSH key data")

        SideEffectAdapter.dispatch_add_ssh_key(self, key_name, key_content)

        ssh_key = DBAdapter.add_ssh_key(self, key_name, key_content)
        self.ssh_keys.append(ssh_key)

        return ssh_key