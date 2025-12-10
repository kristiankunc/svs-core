import random
import string

from pathlib import Path
from typing import TYPE_CHECKING

from svs_core.docker.json_properties import Volume
from svs_core.shared.logger import get_logger
from svs_core.shared.shell import create_directory, remove_directory, run_command

if TYPE_CHECKING:
    from svs_core.users.user import User


class SystemVolumeManager:
    """Manages system volumes for users."""

    BASE_PATH = Path("/var/svs/volumes")

    @staticmethod
    def generate_free_volume(user: "User") -> Path:
        """Generates a free volume path for a given user ID.

        Args:
            user (User): The user for whom to generate the volume.

        Returns:
            Path: The path to the generated volume (absolute).

        Raises:
            RuntimeError: If no free volume path is found within the maximum attempts.
        """
        MAX_ATTEMPTS = 50
        attempts = 0

        base = SystemVolumeManager.BASE_PATH
        base_resolved = base.resolve(strict=False)

        while attempts < MAX_ATTEMPTS:
            volume_id = "".join(
                random.choice(string.ascii_lowercase) for _ in range(16)
            )
            volume_path = base_resolved / str(user.id) / volume_id
            if not volume_path.exists():
                create_directory(volume_path.as_posix())
                # Set owner to the user and group to svs-admins (requires root)
                run_command(
                    f"sudo chown {user.name}:svs-admins {volume_path.as_posix()}",
                    check=True,
                )
                # Set permissions to allow owner and group full access (770)
                run_command(
                    f"sudo chmod 770 {volume_path.as_posix()}",
                    check=True,
                )

                return volume_path

            attempts += 1

        raise RuntimeError("No free volume path found")

    @staticmethod
    def delete_user_volumes(user_id: int) -> None:
        """Deletes all volumes associated with a given user ID.

        Args:
            user_id (int): The user ID whose volumes are to be deleted.
        """
        get_logger(__name__).info(f"Deleting all volumes for user ID: {user_id}")

        user_path = SystemVolumeManager.BASE_PATH / str(user_id)
        if user_path.exists() and user_path.is_dir():
            get_logger(__name__).debug(f"Removing volume directory: {user_path}")
            remove_directory(user_path.as_posix())
            get_logger(__name__).info(
                f"Successfully deleted volumes for user ID: {user_id}"
            )
        else:
            get_logger(__name__).debug(f"No volumes found for user ID: {user_id}")

    @staticmethod
    def delete_volume(volume_path: Path) -> None:
        """Deletes a specific volume.

        Args:
            volume_path (Path): The path to the volume to be deleted.
        """
        get_logger(__name__).debug(f"Deleting volume: {volume_path}")

        if volume_path.exists() and volume_path.is_dir():
            remove_directory(volume_path.as_posix())
            get_logger(__name__).debug(f"Successfully deleted volume: {volume_path}")
        else:
            get_logger(__name__).debug(f"Volume not found: {volume_path}")

    @staticmethod
    def find_host_path(container_path: Path, volumes: list[Volume]) -> Path | None:
        """Finds the host path corresponding to a given container path.

        Args:
            container_path (Path): The container path to search for.
            volumes (list[Volume]): The list of volume mappings.

        Returns:
            Path | None: The corresponding host path if found, otherwise None.
        """

        for volume in volumes:
            vol_container_path = Path(volume.container_path).resolve()
            try:
                if container_path.resolve().is_relative_to(vol_container_path):
                    if volume.host_path is not None:
                        host_base_path = Path(volume.host_path).resolve()
                        relative_subpath = container_path.resolve().relative_to(
                            vol_container_path
                        )
                        return host_base_path / relative_subpath
            except ValueError:
                continue

        return None
