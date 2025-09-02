from typing import Any

from svs_core.db.models import OrmBase, TemplateModel, TemplateType


class Template(OrmBase):
    _model_cls = TemplateModel

    def __init__(self, model: TemplateModel, **_: Any):
        super().__init__(model)
        self._model: TemplateModel = model

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def type(self) -> TemplateType:
        return self._model.type

    @property
    def image(self) -> str | None:
        return self._model.image

    @property
    def dockerfile(self) -> str | None:
        return self._model.dockerfile

    @property
    def description(self) -> str | None:
        return self._model.description

    @property
    def default_env(self) -> dict[str, str]:
        return self._model.default_env or {}

    @property
    def default_ports(self) -> list[dict[str, Any]]:
        return self._model.default_ports or []

    @property
    def default_volumes(self) -> list[dict[str, Any]]:
        return self._model.default_volumes or []

    @property
    def start_cmd(self) -> str | None:
        return self._model.start_cmd

    @property
    def healthcheck(self) -> dict[str, Any]:
        return self._model.healthcheck or {}

    @property
    def labels(self) -> dict[str, str]:
        return self._model.labels or {}

    @property
    def args(self) -> dict[str, str]:
        return self._model.args or {}

    def __str__(self) -> str:
        return (
            f"Template(id={self.id}, name={self.name}, type={self.type}, image={self.image}, "
            f"dockerfile={self.dockerfile}, description={self.description}, default_env={self.default_env}, "
            f"default_ports={self.default_ports}, default_volumes={self.default_volumes}, start_cmd={self.start_cmd}, "
            f"healthcheck={self.healthcheck}, labels={self.labels}, args={self.args})"
        )

    @classmethod
    async def create(
        cls,
        name: str,
        type: TemplateType = TemplateType.IMAGE,
        image: str | None = None,
        dockerfile: str | None = None,
        description: str | None = None,
        default_env: dict[str, str] | None = None,
        default_ports: list[dict[str, Any]] | None = None,
        default_volumes: list[dict[str, Any]] | None = None,
        start_cmd: str | None = None,
        healthcheck: dict[str, Any] | None = None,
        labels: dict[str, str] | None = None,
        args: dict[str, str] | None = None,
    ) -> "Template":
        """Creates a new template with all supported attributes."""
        name = name.strip()
        if not name:
            raise ValueError("Template name cannot be empty")

        model = await TemplateModel.create(
            name=name,
            type=type,
            image=image,
            dockerfile=dockerfile,
            description=description,
            default_env=default_env,
            default_ports=default_ports,
            default_volumes=default_volumes,
            start_cmd=start_cmd,
            healthcheck=healthcheck,
            labels=labels,
            args=args,
        )
        return cls(model=model)

    @classmethod
    async def import_from_json(cls, data: dict[str, Any]) -> "Template":
        """
        Creates a Template instance from a JSON/dict object.
        Relies on the existing create factory method.
        """
        return await cls.create(
            name=data.get("name", ""),
            type=TemplateType(data.get("type", "image")),
            image=data.get("image"),
            dockerfile=data.get("dockerfile"),
            description=data.get("description"),
            default_env=data.get("default_env"),
            default_ports=data.get("default_ports"),
            default_volumes=data.get("default_volumes"),
            start_cmd=data.get("start_cmd"),
            healthcheck=data.get("healthcheck"),
            labels=data.get("labels"),
            args=data.get("args"),
        )
