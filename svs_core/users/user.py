from svs_core.db.constructable import ConstructableFromORM
from svs_core.users.ssh_key import SSHKey
from typing import Optional, cast
from svs_core.db.models import User as UserModel



class User(ConstructableFromORM):
    def __init__(self,
                 id: int,
                 name: str,
                 ssh_keys: Optional[list[SSHKey]] = None,
                 *,
                 _orm_check: bool = False):
        super().__init__(_orm_check=_orm_check)

        self.id = id
        self.name = name
        self.ssh_keys = ssh_keys or []

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
