from typing import Any

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
    def container_id(self) -> str | None:
        return self._model.container_id

    @property
    def image(self) -> str | None:
        return self._model.image

    @property
    def domain(self) -> str | None:
        return self._model.domain

    @property
    def env(self) -> dict[str, str]:
        return self._model.env or {}

    @property
    def exposed_ports(self) -> list[dict[str, Any]]:
        return self._model.exposed_ports or []

    @property
    def volumes(self) -> list[dict[str, Any]]:
        return self._model.volumes or []

    @property
    def command(self) -> str | None:
        return self._model.command

    @property
    def labels(self) -> dict[str, str]:
        return self._model.labels or {}

    @property
    def args(self) -> dict[str, str]:
        return self._model.args or {}

    @property
    def healthcheck(self) -> dict[str, Any]:
        return self._model.healthcheck or {}

    @property
    def networks(self) -> list[str]:
        return self._model.networks or []

    @property
    def status(self) -> str | None:
        return self._model.status

    @property
    def exit_code(self) -> int | None:
        return self._model.exit_code

    @property
    def template(self) -> Template:
        return Template(model=self._model.template)

    @property
    def user(self) -> User:
        return User(model=self._model.user)

    def __str__(self) -> str:
        return (
            f"Service(id={self.id}, name={self.name}, domain={self.domain}, "
            f"container_id={self.container_id}, image={self.image}, exposed_ports={self.exposed_ports}, "
            f"env={self.env}, volumes={self.volumes}, command={self.command}, "
            f"healthcheck={self.healthcheck}, labels={self.labels}, args={self.args}, networks={self.networks}, "
            f"status={self.status}, exit_code={self.exit_code}, template={self.template}, user={self.user})"
        )

    @classmethod
    async def create(
        cls,
        name: str,
        template_id: int,
        user_id: int,
        domain: str | None = None,
        container_id: str | None = None,
        image: str | None = None,
        exposed_ports: list[dict[str, Any]] | None = None,
        env: dict[str, str] | None = None,
        volumes: list[dict[str, Any]] | None = None,
        command: str | None = None,
        healthcheck: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        args: dict[str, str] | None = None,
        networks: list[str] | None = None,
        status: str | None = None,
        exit_code: int | None = None,
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
            image=image,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            command=command,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
            networks=networks,
            status=status,
            exit_code=exit_code,
        )
        return cls(model=model)
