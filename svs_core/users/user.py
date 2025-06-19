from typing import Optional

from svs_core.db.models import OrmBase, UserModel


class User(OrmBase):
    _model_cls = UserModel

    def __init__(self, model: UserModel, name: str, email: str, password_raw: str):
        super().__init__(model)
        self._model = model
        self.name = name
        self.email = email
        self.password = password_raw  # TODO: hash password

    @classmethod
    async def create(cls, name: str, email: str, password_raw: str) -> "User":
        model = UserModel(name=name, email=email, password=password_raw)
        await model.save()
        return cls(model=model, name=name, email=email, password_raw=password_raw)

    @classmethod
    async def get_by_email(cls, email: str) -> Optional["User"]:
        return await cls._get("email", email)
