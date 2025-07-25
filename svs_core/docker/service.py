from typing import Any, Optional

from svs_core.db.models import OrmBase, ServiceModel
from svs_core.docker.template import Template
from svs_core.users.user import User


class Service(OrmBase):
    _model_cls = ServiceModel

    def __init__(self, model: ServiceModel, **_: Any):
        super().__init__(model)
        self._model: ServiceModel = model

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def container_id(self) -> Optional[str]:
        return self._model.container_id

    @property
    def domain(self) -> Optional[str]:
        return self._model.domain

    @property
    def template(self) -> Template:
        return Template(model=self._model.template)

    @property
    def user(self) -> User:
        return User(model=self._model.user)

    def __str__(self) -> str:
        return f"Service(name={self.name}, domain={self.domain}, template={self.template}, user={self.user})"

    @classmethod
    async def create(
        cls,
        name: str,
        template_id: int,
        user_id: int,
        domain: Optional[str] = None,
    ) -> "Service":
        """
        Creates a new service with the given name, template, user, and optional container_id and domain.
        Args:
            name (str): The name of the service.
            template_id (int): The ID of the template to use for the service.
            user_id (int): The ID of the user who owns the service.
            domain (Optional[str]): The domain for the service.
        Returns:
            Service: The created service instance.
        """
        name = name.strip()
        model = await ServiceModel.create(
            name=name,
            template_id=template_id,
            user_id=user_id,
            domain=domain,
        )
        return cls(model=model)
