from typing import Any, Optional

from svs_core.db.models import OrmBase, UserModel
from svs_core.shared.hash import hash_password


class User(OrmBase):
    _model_cls = UserModel

    def __init__(
        self, model: UserModel, name: str, email: str, password: str, **_: Any
    ):
        super().__init__(model)
        self._model = model
        self.name = name
        self.email = email
        self.password = password

    @classmethod
    async def create(cls, name: str, email: str, password: str) -> "User":
        model = UserModel(name=name, email=email, password=hash_password(password))
        await model.save()
        return cls(model=model, name=name, email=email, password=model.password)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        return await cls._get("email", email)
