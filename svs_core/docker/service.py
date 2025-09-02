from typing import Any, List

from svs_core.db.models import OrmBase, ServiceModel
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
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
    def env(self) -> List[EnvVariable]:
        env_dict = self._model.env or {}
        return [EnvVariable(key=key, value=value) for key, value in env_dict.items()]

    @property
    def exposed_ports(self) -> List[ExposedPort]:
        ports_list = self._model.exposed_ports or []
        result = []
        for port in ports_list:
            container_port = port.get("container")
            if container_port is not None:  # container_port is required
                result.append(
                    ExposedPort(
                        container_port=int(container_port),
                        host_port=(
                            int(port["host"]) if port.get("host") is not None else None
                        ),
                    )
                )
        return result

    @property
    def volumes(self) -> List[Volume]:
        volumes_list = self._model.volumes or []
        result = []
        for volume in volumes_list:
            container_path = volume.get("container")
            if container_path is not None:  # container_path is required
                result.append(
                    Volume(
                        container_path=str(container_path),
                        host_path=(
                            str(volume["host"])
                            if volume.get("host") is not None
                            else None
                        ),
                    )
                )
        return result

    @property
    def command(self) -> str | None:
        return self._model.command

    @property
    def labels(self) -> List[Label]:
        labels_dict = self._model.labels or {}
        return [Label(key=key, value=value) for key, value in labels_dict.items()]

    @property
    def args(self) -> list[str]:
        return self._model.args or []

    @property
    def healthcheck(self) -> Healthcheck | None:
        healthcheck_dict = self._model.healthcheck or {}
        if not healthcheck_dict or "test" not in healthcheck_dict:
            return None

        return Healthcheck(
            test=healthcheck_dict.get("test", []),
            interval=healthcheck_dict.get("interval"),
            timeout=healthcheck_dict.get("timeout"),
            retries=healthcheck_dict.get("retries"),
            start_period=healthcheck_dict.get("start_period"),
        )

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
        env_vars = [f"{env.key}={env.value}" for env in self.env]
        ports = [
            f"{port.container_port}:{port.host_port}" for port in self.exposed_ports
        ]
        volumes = [
            f"{vol.container_path}:{vol.host_path or 'None'}" for vol in self.volumes
        ]
        labels = [f"{label.key}={label.value}" for label in self.labels]

        healthcheck_str = "None"
        if self.healthcheck:
            test_str = " ".join(self.healthcheck.test)
            healthcheck_str = f"test='{test_str}'"

        return (
            f"Service(id={self.id}, name={self.name}, domain={self.domain}, "
            f"container_id={self.container_id}, image={self.image}, "
            f"exposed_ports=[{', '.join(ports)}], "
            f"env=[{', '.join(env_vars)}], "
            f"volumes=[{', '.join(volumes)}], "
            f"command={self.command}, "
            f"healthcheck={healthcheck_str}, "
            f"labels=[{', '.join(labels)}], "
            f"args={self.args}, networks={self.networks}, "
            f"status={self.status}, exit_code={self.exit_code}, "
            f"template={self.template}, user={self.user})"
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
        args: list[str] | None = None,
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

        container = DockerContainerManager.create_container(
            name=name,
            image=image or model.template.image,
            command=command or model.template.start_cmd,
            args=args or model.template.args,
        )

        model.container_id = container.id
        await model.save()

        return cls(model=model)
