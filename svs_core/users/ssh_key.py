from svs_core.db.constructable import ConstructableFromORM
from svs_core.users.user import User
from typing import Optional, cast
from svs_core.db.models import SSHKey as SSHKeyModel

class SSHKey(ConstructableFromORM):
    def __init__(
            self,
            id: int,
            name: str,
            content: str,
            user: Optional[User] = None,
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
            user=cast(Optional[User], kwargs.get("user")),
            _orm_check=True,
        )
