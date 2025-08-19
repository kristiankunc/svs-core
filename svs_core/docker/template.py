from typing import Any, Optional

from svs_core.db.models import OrmBase, TemplateModel
from svs_core.shared.github import destruct_github_url
from svs_core.shared.http import send_http_request


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
    def exposed_ports(self) -> Optional[Any]:
        return self._model.exposed_ports

    def __str__(self) -> str:
        return f"Template(id={self.id}, name={self.name}, description={self.description}, exposed_ports={self.exposed_ports})"

    @classmethod
    async def create(
        cls,
        name: str,
        dockerfile: str,
        description: Optional[str] = None,
        exposed_ports: Optional[list[int]] = None,
    ) -> "Template":
        """Creates a new template with the given name, dockerfile, description, and exposed ports.

        Args:
            name (str): The name of the template.
            dockerfile (str): The Dockerfile content.
            description (Optional[str]): A description of the template.
            exposed_ports (Optional[list[int]]): A list of exposed ports.
        Returns:
            Template: The created template instance.
        Raises:
            ValueError: If the name or dockerfile is empty.
        """
        name = name.lower().strip()
        dockerfile = dockerfile.strip()

        if not name or not dockerfile:
            raise ValueError("Provided values cannot be empty")

        model = await TemplateModel.create(
            name=name,
            dockerfile=dockerfile,
            description=description,
            exposed_ports=exposed_ports,
        )

        return cls(model=model)

    @classmethod
    async def parse_dockerfile(
        cls, dockerfile: str
    ) -> tuple[str, Optional[str], list[int]]:
        """Parses a Dockerfile to extract the name, description, and exposed ports.

        Args:
            dockerfile (str): The Dockerfile content.
        Returns:
            tuple[str, Optional[str], list[int]]: A tuple containing the name, description, and exposed ports.
        """
        lines = dockerfile.splitlines()
        name = None
        description = None
        exposed_ports: list[int] = []

        for line in lines:
            line = line.strip()
            if line.startswith("# NAME="):
                name = line[len("# NAME=") :].strip()
            elif line.startswith("# DESCRIPTION="):
                description = line[len("# DESCRIPTION=") :].strip()
            elif line.startswith("# PROXY_PORTS="):
                ports = line[len("# PROXY_PORTS=") :].strip().split(",")
                exposed_ports.extend(
                    int(port.strip()) for port in ports if port.strip().isdigit()
                )

        if not name:
            raise ValueError("Dockerfile does not have a valid name.")

        return name, description, exposed_ports

    @classmethod
    async def import_from_url(cls, url: str) -> "Template":
        """Imports a template from a URL.

        Args:
            url (str): The URL of the Dockerfile.
        Returns:
            Template: The imported template.
        Raises:
            ValueError: If the URL is invalid or does not point to a Dockerfile.
        """
        response = await send_http_request(method="GET", url=url)
        if response.status_code != 200:
            raise ValueError(f"Failed to fetch Dockerfile from {url}")

        dockerfile_content = response.text
        name, description, exposed_ports = await cls.parse_dockerfile(
            dockerfile_content
        )

        return await cls.create(
            name=name,
            dockerfile=dockerfile_content,
            description=description,
            exposed_ports=exposed_ports,
        )

    @classmethod
    async def discover_from_github(cls, repo_url: str) -> list["Template"]:
        """Discovers a template from a GitHub repository.

        Args:
            repo_url (str): The URL of the GitHub repository.
        Returns:
            list[Template]: The discovered templates.
        Raises:
            ValueError: If the repository URL is invalid or does not contain a Dockerfile.
        """

        repo = destruct_github_url(repo_url)
        response = await send_http_request(
            method="GET",
            url=f"https://api.github.com/repos/{repo.owner}/{repo.name}/contents/{repo.path or ''}",
        )
        directory_contents = response.json()

        if isinstance(directory_contents, dict):
            directory_contents = [directory_contents]

        templates: list["Template"] = []
        for file in directory_contents:
            if file["name"].endswith(".Dockerfile"):
                file_content = (
                    await send_http_request(method="GET", url=file["download_url"])
                ).text

                # Use the parse_dockerfile method to extract details
                name, description, exposed_ports = await cls.parse_dockerfile(
                    file_content
                )

                templates.append(
                    await cls.create(
                        name=name,
                        dockerfile=file_content,
                        description=description,
                        exposed_ports=exposed_ports,
                    )
                )

        return templates
