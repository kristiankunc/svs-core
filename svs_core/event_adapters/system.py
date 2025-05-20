import logging
from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command
from svs_core.users.user import User
from svs_core.users.ssh_key import SSHKey


class SystemAdapter(SideEffectAdapter):
    """
    SystemAdapter is a side effect adapter that interacts with the system to perform operations
    """

    def _create_user(self, username: str) -> None:
        """
        Creates a new user in the system.

        Args:
            username (str): The username to create.
        """

        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        run_command(f"sudo useradd -m {username}")
        run_command(f"sudo chmod 400 /home/{username}/.ssh/authorized_keys")

        get_logger(__name__).log(logging.INFO, f"User {username} created")

    def _delete_user(self, user: User) -> None:
        """
        Deletes a user from the system.

        Args:
            user (User): The user to delete.
        """

        get_logger(__name__).log(logging.INFO, f"Deleting user {user.name}")

        run_command(f"sudo userdel -r {user.name}")

        get_logger(__name__).log(logging.INFO, f"User {user.name} deleted")

    def _add_ssh_key(self, user: User, key_name: str, key_content: str) -> None:
        """
        Adds an SSH key to the user's authorized keys.

        Args:
            user (User): The user to add the SSH key for.
            key_name (str): The name of the SSH key.
            key_content (str): The content of the SSH key (public key).
        """

        get_logger(__name__).log(logging.INFO, f"Adding SSH key for user {user.name}")

        run_command(f"sudo mkdir -p /home/{user.name}/.ssh")
        run_command(
            f"echo '{key_content}' | sudo tee -a /home/{user.name}/.ssh/authorized_keys"
        )
        run_command(
            f"sudo chown {user.name}:{user.name} /home/{user.name}/.ssh/authorized_keys"
        )
        run_command(f"sudo chmod 400 /home/{user.name}/.ssh/authorized_keys")

        get_logger(__name__).log(logging.INFO, f"SSH key added for user {user.name}")

    def _delete_ssh_key(self, user: User, ssh_key: SSHKey) -> None:
        """
        Deletes an SSH key from the user's authorized keys.

        Args:
            user (User): The user to delete the SSH key for.
            ssh_key (SSHKey): The SSH key to delete.
        """

        get_logger(__name__).log(logging.INFO, f"Deleting SSH key for user {user.name}")

        run_command(
            f"sudo sed -i '/{ssh_key.content}/d' /home/{user.name}/.ssh/authorized_keys"
        )

        get_logger(__name__).log(logging.INFO, f"SSH key deleted for user {user.name}")
