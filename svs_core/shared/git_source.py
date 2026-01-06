from pathlib import Path

from svs_core.db.models import GitSourceModel
from svs_core.shared.http import is_url
from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class GitSource(GitSourceModel):
    """Service class representing a service in the system."""

    class Meta:  # noqa: D106
        proxy = True

    class InvalidGitSourceError(ValueError):
        """Exception raised for invalid GitSource parameters."""

    @classmethod
    def create(
        cls,
        service_id: int,
        repository_url: str,
        destination_path: Path,
        branch: str = "main",
    ) -> "GitSource":
        """Create a new GitSource instance.

        Args:
            repository_url (str): The URL of the Git repository.
            destination_path (Path): The destination path where the repository will be cloned.
            branch (str, optional): The branch to checkout. Defaults to "main".

        Returns:
            GitSource: The created GitSource instance.

        Raises:
            ValueError: If any of the input parameters are invalid.
            Service.DoesNotExist: If the service with the given ID does not exist.
        """
        from svs_core.docker.service import Service

        Service.objects.get(id=service_id)

        if not destination_path.is_absolute():
            raise ValueError("destination_path must be an absolute path")

        if not is_url(repository_url):
            raise ValueError("repository_url must be a valid URL")

        if branch.strip() == "" or " " in branch:
            raise ValueError("branch cannot be an empty string or contain spaces")

        git_source = cls(
            service_id=service_id,
            repository_url=repository_url,
            destination_path=str(destination_path),
            branch=branch,
        )
        git_source.save()
        return git_source

    def execute(self) -> None:
        """Execute the git clone operation for this GitSource."""

        get_logger().info(
            f"Cloning repository {self.repository_url} (branch: {self.branch}) to {self.destination_path}"
        )

        run_command(
            f"git clone --branch {self.branch} {self.repository_url} {self.destination_path}"
        )

        get_logger().info(
            f"Successfully cloned repository {self.repository_url} to {self.destination_path}"
        )

    def __str__(self) -> str:
        return f"GitSource(id={self.id}, repository_url={self.repository_url}, branch={self.branch}, destination_path={self.destination_path})"
