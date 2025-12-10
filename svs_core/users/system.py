import getpass
import grp
import os
import pwd

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class SystemUserManager:
    """Class for managing system users."""

    @staticmethod
    def create_user(
        username: str, password: str, admin: bool = False, shell_path: str = "/bin/bash"
    ) -> None:
        """Creates a system user with the given username and password.

        Args:
            username (str): The username for the new system user.
            password (str): The password for the new system user.
            admin (bool, optional): Whether to add the user to the admin group. Defaults to False.
            shell_path (str, optional): The login shell for the new user. Defaults to "/bin/bash".
        """
        get_logger(__name__).info(f"Creating system user '{username}' (admin: {admin})")

        try:
            run_command(
                f"sudo adduser --shell {shell_path} --disabled-password --gecos '' {username}",
                check=True,
            )
            run_command(f"echo '{username}:{password}' | sudo chpasswd", check=True)

            # run_command(f"sudo usermod -aG svs-users {username}", check=True)

            if admin:
                run_command(f"sudo usermod -aG svs-admins {username}", check=True)

            get_logger(__name__).info(
                f"Successfully created {'admin' if admin else 'standard'} system user: {username}"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to create system user '{username}': {str(e)}"
            )
            raise

    @staticmethod
    def delete_user(username: str) -> None:
        """Deletes the system user with the given username.

        Args:
            username (str): The username of the system user to delete.
        """
        get_logger(__name__).info(f"Deleting system user '{username}'")

        try:
            run_command(f"sudo userdel -r {username}", check=True)
            get_logger(__name__).info(f"Successfully deleted system user: {username}")
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to delete system user '{username}': {str(e)}"
            )
            raise

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
        """Returns the username of whoever is running the process.

        Handles sudo, su, and direct execution correctly.
        For sudo: uses SUDO_USER env var (set by sudo)
        For su: uses effective UID via pwd
        For direct execution: uses getpass.getuser()
        """
        # For sudo execution, SUDO_USER contains the original user
        if "SUDO_USER" in os.environ and os.environ["SUDO_USER"]:
            return os.environ["SUDO_USER"]

        # Return the actual effective user (UID)
        try:
            return pwd.getpwuid(os.geteuid()).pw_name
        except Exception:
            pass

        try:
            return os.getlogin()
        except Exception:
            pass

        return getpass.getuser()

    @staticmethod
    def add_ssh_key_to_user(username: str, ssh_key: str) -> None:
        """Adds an SSH public key to the specified user's authorized_keys.

        Args:
            username (str): The username of the system user.
            ssh_key (str): The SSH public key to add.
        """
        user_info = pwd.getpwnam(username)
        ssh_dir = os.path.join(user_info.pw_dir, ".ssh")
        authorized_keys_file = os.path.join(ssh_dir, "authorized_keys")

        run_command(f"sudo mkdir -p {ssh_dir}", check=True)
        run_command(f"sudo chown {username}:{username} {ssh_dir}", check=True)
        run_command(f"sudo chmod 700 {ssh_dir}", check=True)

        with open("/tmp/temp_authorized_keys", "w") as temp_file:
            temp_file.write(ssh_key + "\n")

        run_command(
            f"sudo bash -c 'cat /tmp/temp_authorized_keys >> {authorized_keys_file}'",
            check=True,
        )

        run_command(
            f"sudo chown {username}:{username} {authorized_keys_file}", check=True
        )
        run_command(f"sudo chmod 600 {authorized_keys_file}", check=True)
        run_command("sudo rm /tmp/temp_authorized_keys", check=True)

        get_logger(__name__).info(f"Added SSH key to {username}'s authorized_keys")

    @staticmethod
    def remove_ssh_key_from_user(username: str, ssh_key: str) -> None:
        """Removes an SSH public key from the specified user's authorized_keys.

        Args:
            username (str): The username of the system user.
            ssh_key (str): The SSH public key to remove.
        """
        user_info = pwd.getpwnam(username)
        authorized_keys_file = os.path.join(user_info.pw_dir, ".ssh", "authorized_keys")

        temp_file_path = "/tmp/temp_authorized_keys_remove"

        with open("/tmp/temp_key_to_remove", "w") as temp_key_file:
            temp_key_file.write(ssh_key)

        run_command(
            f"sudo grep -v -f /tmp/temp_key_to_remove {authorized_keys_file} > {temp_file_path}",
            check=False,
        )
        run_command(f"sudo mv {temp_file_path} {authorized_keys_file}", check=True)
        run_command(
            f"sudo chown {username}:{username} {authorized_keys_file}", check=True
        )
        run_command(f"sudo chmod 600 {authorized_keys_file}", check=True)
        run_command("sudo rm /tmp/temp_key_to_remove", check=True)

        get_logger(__name__).info(f"Removed SSH key from {username}'s authorized_keys")

    @staticmethod
    def get_system_uid_gid(username: str) -> tuple[int, int]:
        """Returns the UID and GID of the user running the process.

        Returns:
            tuple[int, int]: A tuple containing the UID and GID.
        """
        uid = run_command(f"sudo id -u {username}", check=True)
        gid = run_command(f"sudo id -g {username}", check=True)
        return int(uid.stdout.strip()), int(gid.stdout.strip())
