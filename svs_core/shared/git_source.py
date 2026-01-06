from pathlib import Path

from svs_core.db.models import GitSourceModel
from svs_core.docker.service import Service
from svs_core.shared.http import is_url


class GitSource(GitSourceModel):
    """Service class representing a service in the system."""

    class Meta:  # noqa: D106
        proxy = True

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
