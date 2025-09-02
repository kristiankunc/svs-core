from typing import Any, Optional

from svs_core.db.models import OrmBase, TemplateModel


class Template(OrmBase):
    _model_cls = TemplateModel

    def __init__(self, model: TemplateModel, **_: Any):
        super().__init__(model)
        self._model: TemplateModel = model

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def dockerfile(self) -> str:
        return self._model.dockerfile

    @property
    def description(self) -> Optional[str]:
        return self._model.description

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

    def __str__(self) -> str:
        return (
            f"Template(id={self.id}, name={self.name}, "
            f"description={self.description}, exposed_ports={self.exposed_ports}, "
            f"env={self.env}, volumes={self.volumes}, entrypoint={self.entrypoint}, "
            f"cmd={self.cmd}, healthcheck={self.healthcheck}, labels={self.labels})"
        )

    @classmethod
    async def create(
        cls,
        name: str,
        dockerfile: str,
        description: Optional[str] = None,
        exposed_ports: Optional[list[int]] = None,
        env: Optional[dict[str, str]] = None,
        volumes: Optional[list[str]] = None,
        entrypoint: Optional[str] = None,
        cmd: Optional[list[str]] = None,
        healthcheck: Optional[dict[str, Any]] = None,
        labels: Optional[dict[str, str]] = None,
    ) -> "Template":
        """Creates a new template with all supported attributes."""
        name = name.lower().strip()
        dockerfile = dockerfile.strip()

        if not name or not dockerfile:
            raise ValueError("Provided values cannot be empty")

        model = await TemplateModel.create(
            name=name,
            dockerfile=dockerfile,
            description=description,
            exposed_ports=exposed_ports,
            env=env,
            volumes=volumes,
            entrypoint=entrypoint,
            cmd=cmd,
            healthcheck=healthcheck,
            labels=labels,
        )

        return cls(model=model)
