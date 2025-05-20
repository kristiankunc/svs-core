from svs_core.db.constructable import ConstructableFromORM
from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.event_adapters.db import DBAdapter
from svs_core.users.user import User
from typing import cast
from svs_core.db.models import SSHKeyModel
import re

class SSHKey(ConstructableFromORM):
    def __init__(
            self,
            id: int,
            name: str,
            content: str,
            user: User,
            *,
            _orm_check: bool = False):
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
    
    def delete(self) -> None:
        self.user.ssh_keys.remove(self)
        
        SideEffectAdapter.dispatch_delete_ssh_key(self.user, self)
        DBAdapter.delete_ssh_key(self.user, self)
        self.user.ssh_keys.remove(self)

        # TODO: destruct

    @staticmethod
    def is_valid(name: str, content: str) -> bool:
        if not name or len(name) > 32:
            return False
        
        ssh_key_pattern = r"^(ssh-(rsa|dss|ed25519|ecdsa) AAAA[0-9A-Za-z+/]+[=]{0,3} .+)|(ecdsa-sha2-nistp[0-9]+ AAAA[0-9A-Za-z+/]+[=]{0,3} .+)$"
        match = re.match(ssh_key_pattern, content)

        return bool(match)

