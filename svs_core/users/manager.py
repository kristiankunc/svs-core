import re
from svs_core.shared.base import Executable


class UserManager(Executable):
    """
    UserManager class to manage user-related operations.

    This class inherits from Executable and provides methods to manage users.
    It includes functionality to add, remove, and list users.

    Attributes:
        logger: Logger instance for logging operations.
    """

    def __init__(self) -> None:
        super().__init__()

    def is_username_valid(self, username: str) -> bool:
        """
        Validates the username against a regex pattern.

        Args:
            username (str): The username to validate.

        Returns:
            bool: True if the username is valid, False otherwise.
        """
        username_regex = r"^[a-z_][a-z0-9_-]{0,30}[a-z0-9_]$"
        return bool(re.match(username_regex, username))

    def user_exists(self, username: str) -> bool:
        """
        Checks if a user exists in the system.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        result = self.execute(f"id -u {username}", check=False)
        return result.returncode == 0

    def create_user(self, name: str) -> None:
        """
        Creates a new user with the specified name.

        Args:
            name (str): The name of the user to create.

        Returns:
            None
        """

        self.logger.info(f"Creating user: {name}")

        if not self.is_username_valid(name):
            self.logger.error(f"Invalid username: {name}")
            raise ValueError(f"Invalid username: {name}")

        if self.user_exists(name):
            self.logger.error(f"User {name} already exists.")
            raise ValueError(f"User {name} already exists.")

        self.execute(f"sudo useradd {name}")
        self.logger.info(f"User {name} created successfully.")

    def delete_user(self, name: str) -> None:
        """
        Deletes the specified user.

        Args:
            name (str): The name of the user to delete.

        Returns:
            None
        """

        self.logger.info(f"Deleting user: {name}")

        if not self.user_exists(name):
            self.logger.error(f"User {name} does not exist.")
            raise ValueError(f"User {name} does not exist.")

        self.execute(f"sudo userdel {name}")
        self.logger.info(f"User {name} deleted successfully.")

    def add_ssh_key(self, username: str, key_name: str, ssh_key: str) -> None:
        """
        Adds an SSH key to the specified user's authorized keys.

        Args:
            username (str): The name of the user.
            key_name (str): The name of the SSH key.
            ssh_key (str): The SSH key to add.

        Returns:
            None
        """

        self.logger.info(f"Adding SSH key for user: {username}")

        if not self.user_exists(username):
            self.logger.error(f"User {username} does not exist.")
            raise ValueError(f"User {username} does not exist.")

        check_auth_keys_cmd = f"sudo test -f /home/{username}/.ssh/authorized_keys"
        result = self.execute(check_auth_keys_cmd, check=False)

        if result.returncode != 0:
            self.execute(f"sudo mkdir -p /home/{username}/.ssh")
            self.execute(f"sudo touch /home/{username}/.ssh/authorized_keys")
            self.execute(
                f"sudo chown {username}:{username} /home/{username}/.ssh/authorized_keys")
            self.execute(f"sudo chmod 600 /home/{username}/.ssh/authorized_keys")

        self.execute(
            f"echo '# {key_name}' | sudo tee -a /home/{username}/.ssh/authorized_keys")
        self.execute(
            f"echo '{ssh_key}' | sudo tee -a /home/{username}/.ssh/authorized_keys")

        self.logger.info(f"SSH key added for user: {username}")

    def remove_ssh_key(self, username: str, key_name: str) -> None:
        """
        Removes an SSH key from the specified user's authorized keys.

        Args:
            username (str): The name of the user.
            key_name (str): The name of the SSH key to remove.

        Returns:
            None
        """

        self.logger.info(f"Removing SSH key for user: {username}")

        if not self.user_exists(username):
            self.logger.error(f"User {username} does not exist.")
            raise ValueError(f"User {username} does not exist.")

        check_auth_keys_cmd = f"sudo test -f /home/{username}/.ssh/authorized_keys"
        result = self.execute(check_auth_keys_cmd, check=False)

        if result.returncode != 0:
            self.logger.error(f"No authorized keys file found for user {username}.")
            raise ValueError(f"No authorized keys file found for user {username}.")

        sed_cmd = (
            f"sudo sed -i '/^# {re.escape(key_name)}$/{{N;d;}}' /home/{username}/.ssh/authorized_keys"
        )
        sed_cmd = (
            f"sudo sed -i '/^# {key_name}$/{{N;d;}}' /home/{username}/.ssh/authorized_keys"
        )
        self.execute(sed_cmd)

        self.logger.info(f"SSH key removed for user: {username}")
