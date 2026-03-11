from dataclasses import dataclass
from importlib.metadata import version
from typing import Callable

from svs_core.docker.service import Service
from svs_core.shared.logger import get_logger


@dataclass
class PackageVersion:
    """Class representing the package version.

    It parses a format of "major.minor.patch" and provides comparison
    capabilities.
    """

    """Entire version string as provided."""
    string: str
    """Major version number."""
    major: int
    """Minor version number."""
    minor: int
    """Patch version number."""
    patch: int

    def __init__(self, version_str: str):
        self.string = version_str
        parts = version_str.split(".")

        if len(parts) != 3:
            raise ValueError(
                f"Invalid version format: '{version_str}'. Expected format 'major.minor.patch'."
            )

        try:
            self.major = int(parts[0])
            self.minor = int(parts[1])
            self.patch = int(parts[2])
        except ValueError as e:
            raise ValueError(
                f"Invalid version format: '{version_str}'. Expected format 'major.minor.patch'."
            ) from e

    def _as_tuple(self) -> tuple[int, int, int]:
        """Convert version to tuple for comparison."""
        return (self.major, self.minor, self.patch)

    def __lt__(self, other: "PackageVersion") -> bool:
        """Check if this version is less than another."""
        return self._as_tuple() < other._as_tuple()

    def __le__(self, other: "PackageVersion") -> bool:
        """Check if this version is less than or equal to another."""
        return self._as_tuple() <= other._as_tuple()

    def __gt__(self, other: "PackageVersion") -> bool:
        """Check if this version is greater than another."""
        return self._as_tuple() > other._as_tuple()

    def __ge__(self, other: "PackageVersion") -> bool:
        """Check if this version is greater than or equal to another."""
        return self._as_tuple() >= other._as_tuple()

    def __eq__(self, other: object) -> bool:
        """Check if this version equals another."""
        if not isinstance(other, PackageVersion):
            return NotImplemented
        return self._as_tuple() == other._as_tuple()


@dataclass
class Migration:
    """Class representing a system migration."""

    """Migration name."""
    name: str
    """Migration version.

    When this or any higher version is reached, the migration will be
    executed.
    """
    version: PackageVersion
    """Migration execution function."""
    run: Callable[[], None]


class Migrator:
    """Class responsible for handling system migrations."""

    migrations: list[Migration]

    @staticmethod
    def get_current_package_version() -> PackageVersion:
        """Get the current package version as a PackageVersion instance.

        Returns:
            PackageVersion: The current package version.
        """

        return PackageVersion(version("svs-core"))

    @staticmethod
    def run(last_known_version: PackageVersion) -> None:
        """Run migrations for versions newer than the last known version.

        Args:
            last_known_version: A PackageVersion instance of the last known version.
        """
        current_version = Migrator.get_current_package_version()
        get_logger(__name__).debug(
            f"Running migrations - current package version: {current_version.string}, Last known version: {last_known_version.string}"
        )

        for migration in Migrator.migrations:
            if (
                current_version >= migration.version
                and migration.version > last_known_version
            ):
                get_logger(__name__).info(f"Running migration: {migration.name}")
                migration.run()

    @staticmethod
    def _restart_policy_change() -> None:
        services = Service.objects.all()
        for service in services:
            service.recreate()


Migrator.migrations = [
    Migration(
        "restart-policy-change",
        PackageVersion("0.14.0"),
        Migrator._restart_policy_change,
    ),
]
