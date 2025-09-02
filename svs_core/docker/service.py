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
    def exposed_ports(self) -> Optional[list[int]]:
        return self._model.exposed_ports

    @property
    def env(self) -> Optional[dict[str, str]]:
        return self._model.env

    @property
    def volumes(self) -> Optional[list[str]]:
        return self._model.volumes

    @property
    def entrypoint(self) -> Optional[str]:
        return self._model.entrypoint

    @property
    def cmd(self) -> Optional[list[str]]:
        return self._model.cmd

    @property
    def healthcheck(self) -> Optional[dict[str, Any]]:
        return self._model.healthcheck

    @property
    def labels(self) -> Optional[dict[str, str]]:
        return self._model.labels

    @property
    def template(self) -> Template:
        return Template(model=self._model.template)

    @property
    def user(self) -> User:
        return User(model=self._model.user)

    def __str__(self) -> str:
        return (
            f"Service(id={self.id}, name={self.name}, domain={self.domain}, "
            f"container_id={self.container_id}, exposed_ports={self.exposed_ports}, "
            f"env={self.env}, volumes={self.volumes}, entrypoint={self.entrypoint}, "
            f"cmd={self.cmd}, healthcheck={self.healthcheck}, labels={self.labels}, "
            f"template={self.template}, user={self.user})"
        )

    @classmethod
    async def create(
        cls,
        name: str,
        template_id: int,
        user_id: int,
        domain: Optional[str] = None,
        container_id: Optional[str] = None,
        exposed_ports: Optional[list[int]] = None,
        env: Optional[dict[str, str]] = None,
        volumes: Optional[list[str]] = None,
        entrypoint: Optional[str] = None,
        cmd: Optional[list[str]] = None,
        healthcheck: Optional[dict[str, Any]] = None,
        labels: Optional[dict[str, str]] = None,
    ) -> "Service":
        """Creates a new service with all supported attributes."""
        name = name.strip()
        if not name:
            raise ValueError("Service name cannot be empty")

        model = await ServiceModel.create(
            name=name,
            template_id=template_id,
            user_id=user_id,
            domain=domain,
            container_id=container_id,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            entrypoint=entrypoint,
            cmd=cmd,
            healthcheck=healthcheck,
            labels=labels,
        )
        return cls(model=model)
