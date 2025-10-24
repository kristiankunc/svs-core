import getpass
import os
import pwd

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class SystemUserManager:
    """Class for managing system users."""

    @staticmethod
    def create_user(username: str, password: str, admin: bool = False) -> None:
        """Creates a system user with the given username and password.

        Args:
            username (str): The username for the new system user.
            password (str): The password for the new system user.
            admin (bool, optional): Whether to add the user to the admin group. Defaults to False.
        """
        run_command(f"sudo useradd -m {username}", check=True)
        run_command(f"echo '{username}:{password}' | sudo chpasswd", check=True)
        # run_command(f"sudo usermod -aG svs-users {username}", check=True)

        if admin:
            run_command(f"sudo usermod -aG svs-admins {username}", check=True)

        get_logger(__name__).info(
            f"Created {'admin' if admin else 'standard'} system user: {username}"
        )

    @staticmethod
    def delete_user(username: str) -> None:
        """Deletes the system user with the given username.

        Args:
            username (str): The username of the system user to delete.
        """
        run_command(f"sudo userdel -r {username}", check=True)
        get_logger(__name__).info(f"Deleted system user: {username}")

    @staticmethod
    def is_user_in_group(username: str, groupname: str) -> bool:
        """Checks if a system user is in a specific group.

        Args:
            username (str): The username of the system user.
            groupname (str): The name of the group to check.

        Returns:
            bool: True if the user is in the group, False otherwise.
        """
        result = run_command(f"groups {username} | grep -qw {groupname}", check=False)
        return result.returncode == 0

    @staticmethod
    def get_system_username() -> str:
        """Returns the username of the user who initiated the session.

        Attempts to grab the user if ran by sudo.
        """

        try:
            return os.getlogin()
        except OSError:
            if "SUDO_USER" in os.environ:
                return os.environ["SUDO_USER"]

            try:
                return pwd.getpwuid(os.getuid()).pw_name
            except Exception:
                return getpass.getuser()

        except Exception as e:
            raise RuntimeError("Failed to get current user") from e
