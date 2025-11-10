import random
import string

from pathlib import Path
from typing import TYPE_CHECKING

from svs_core.docker.json_properties import Volume
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
                # Set owner to the user and group to svs-admins
                run_command(
                    f"chown {user.name}:svs-admins {volume_path.as_posix()}",
                    use_svs_user=False,
                )
                # Set permissions to allow owner and group full access (770)
                run_command(f"chmod 770 {volume_path.as_posix()}", use_svs_user=False)

                return volume_path

            attempts += 1

        raise RuntimeError("No free volume path found")

    @staticmethod
    def delete_user_volumes(user_id: int) -> None:
        """Deletes all volumes associated with a given user ID.

        Args:
            user_id (int): The user ID whose volumes are to be deleted.
        """
        user_path = SystemVolumeManager.BASE_PATH / str(user_id)
        if user_path.exists() and user_path.is_dir():
            remove_directory(user_path.as_posix())

    @staticmethod
    def delete_volume(volume_path: Path) -> None:
        """Deletes a specific volume.

        Args:
            volume (Volume): The volume to be deleted.
        """
        if volume_path.exists() and volume_path.is_dir():
            remove_directory(volume_path.as_posix())
