from datetime import datetime, timezone
from pathlib import Path

from svs_core.db.models import GitSourceModel, miscelanous_str_injector
from svs_core.shared.exceptions import ValidationException
from svs_core.shared.http import is_url
from svs_core.shared.logger import get_logger
from svs_core.shared.shell import create_directory, run_command
from svs_core.shared.text import indentate


class GitSource(GitSourceModel):
    """GitSource class representing a Git source repository."""

    class Meta:  # noqa: D106
        proxy = True

    class InvalidGitSourceError(ValidationException):
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
            ValidationException: If any of the input parameters are invalid.
            Service.DoesNotExist: If the service with the given ID does not exist.
        """
        from svs_core.docker.service import Service

        Service.objects.get(id=service_id)

        if not destination_path.is_absolute():
            raise ValidationException("destination_path must be an absolute path")

        if not is_url(repository_url):
            raise ValidationException("repository_url must be a valid URL")

        if branch.strip() == "" or " " in branch:
            raise ValidationException(
                "branch cannot be an empty string or contain spaces"
            )

        git_source = cls(
            service_id=service_id,
            repository_url=repository_url,
            destination_path=str(destination_path),
            branch=branch,
        )
        git_source.save()
        return git_source

    def download(self) -> None:
        """Download the Git repository to the specified destination path."""

        if self.is_cloned():
            return self.update()

        get_logger(__file__).debug(
            f"Cloning repository {self.repository_url} (branch: {self.branch}) to {self.destination_path}"
        )

        dest_path = Path(self.destination_path)

        if not dest_path.parent.exists():
            create_directory(
                dest_path.parent.absolute().as_posix(),
                user=self.service.user.name,
            )

        if dest_path.exists():
            run_command(
                f"find {self.destination_path} -mindepth 1 -delete",
                user=self.service.user.name,
            )
        else:
            create_directory(
                self.destination_path,
                user=self.service.user.name,
            )
        run_command(
            f"git clone --branch {self.branch} {self.repository_url} {self.destination_path}",
            user=self.service.user.name,
        )

        get_logger(__file__).info(
            f"Successfully cloned repository {self.repository_url} to {self.destination_path}"
        )

    def update(self) -> None:
        """Update the Git repository at the destination path."""

        get_logger(__file__).info(
            f"Updating repository {self.repository_url} (branch: {self.branch}) at {self.destination_path}"
        )

        owner = self.service.user.name

        run_command(f"git -C {self.destination_path} fetch", user=owner)
        run_command(
            f"git -C {self.destination_path} checkout {self.branch}", user=owner
        )
        run_command(
            f"git -C {self.destination_path} pull origin {self.branch}", user=owner
        )

        get_logger(__file__).info(
            f"Successfully updated repository {self.repository_url} at {self.destination_path}"
        )

    def is_updated(self) -> bool:
        """Check if the Git source is up to date with remote.

        Returns:
            bool: True if the local repository is up to date, False otherwise.
        """

        from svs_core.shared.shell import run_command

        get_logger(__file__).info(
            f"Checking for updates in repository {self.repository_url} (branch: {self.branch}) at {self.destination_path}"
        )

        if not self.is_cloned():
            get_logger(__file__).debug(
                f"Repository {self.repository_url} is not cloned. Considering it not up to date."
            )
            return False

        owner = self.service.user.name

        run_command(f"git -C {self.destination_path} fetch", user=owner)

        local_commit: str = run_command(
            f"git -C {self.destination_path} rev-parse {self.branch}", user=owner
        ).stdout.strip()
        remote_commit: str = run_command(
            f"git -C {self.destination_path} rev-parse origin/{self.branch}", user=owner
        ).stdout.strip()

        is_up_to_date: bool = local_commit == remote_commit

        if is_up_to_date:
            get_logger(__file__).debug(
                f"Repository {self.repository_url} is up to date."
            )
        else:
            get_logger(__file__).debug(
                f"Repository {self.repository_url} has updates available."
            )

        return is_up_to_date

    def is_cloned(self) -> bool:
        """Check if the Git repository has been cloned to the destination path.

        Returns:
            bool: True if the repository is cloned, False otherwise.
        """

        destination = Path(self.destination_path)
        git_dir = destination / ".git"
        is_cloned = destination.exists() and git_dir.exists() and git_dir.is_dir()

        if is_cloned:
            get_logger(__file__).debug(f"Repository {self.repository_url} is cloned.")
        else:
            get_logger(__file__).debug(
                f"Repository {self.repository_url} is not cloned."
            )

        return is_cloned

    def delete(self) -> None:
        """Delete the GitSource instance.

        Deletes the Git repository at the destination path before
        deleting the instance.
        """
        get_logger(__file__).info(
            f"Deleting Git source {self.repository_url} at {self.destination_path}"
        )
        dest_path = Path(self.destination_path)
        if dest_path.exists():
            run_command(
                f"find {self.destination_path} -mindepth 1 -delete",
                user=self.service.user.name,
            )
        super().delete()

    def __str__(self) -> str:
        return f"GitSource(id={self.id}, repository_url={self.repository_url}, branch={self.branch}, destination_path={self.destination_path}, is_updated={self.is_updated()})"

    def pprint(self, indent: int = 0) -> str:
        """Pretty-print the GitSource details.

        Args:
            indent (int): The indentation level for formatting.

        Returns:
            str: The pretty-printed GitSource details.
        """

        if not self.is_cloned():
            status = "Not cloned"
        elif not self.is_updated():
            status = "Outdated"
        else:
            status = "Up to date"

        return indentate(
            f"""{self.repository_url} @ {self.branch} -> {self.destination_path}
Status: {status}
Miscelaneous:
{miscelanous_str_injector(self, indent=1)}""",
            level=indent,
        )
