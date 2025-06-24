from typing import Any, Optional

from svs_core.db.models import OrmBase, UserModel
from svs_core.shared.hash import hash_password


class User(OrmBase):
    _model_cls = UserModel

    def __init__(self, model: UserModel, name: str, password: str, **_: Any):
        super().__init__(model)
        self._model = model
        self.name = name
        self.password = password

    @classmethod
    async def create(cls, name: str, password: str) -> "User":
        model = UserModel(name=name, password=hash_password(password))
        await model.save()
        return cls(model=model, name=name, password=model.password)

    @classmethod
    async def get_by_name(cls, name: str) -> Optional["User"]:
        return await cls._get("name", name)
