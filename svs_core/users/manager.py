import re

from svs_core.db.client import DBClient
from svs_core.docker.network import DockerNetworkManager
from svs_core.shared.exceptions import UserAlreadyExistsException, UserNotFoundException
from svs_core.shared.logger import get_logger
from svs_core.users.user import User


class UserManager:
    @staticmethod
    def is_username_valid(username: str) -> bool:
        """Checks if the username is valid for linux systems."

        Args:
            username (str): The username to check.

        Returns:
            bool: validity of the username.
        """

        if not 1 <= len(username) <= 32:
            return False

        if not re.match(r"^[a-z_][a-z0-9_-]*[$]?$", username):
            return False

        if username.endswith("-"):
            return False

        return True

    @staticmethod
    def username_exists(username: str) -> bool:
        """Checks if username is already registered in the system.
        Args:
            username (str): The username to check.
        Returns:
            bool: True if the username exists, False otherwise.
        """

        return DBClient.get_user_by_name(username) is not None

    @staticmethod
    def create_user(username: str) -> User:
        """
        Creates a new user in the system.

        Args:
            username (str): The username to create.

        Raises:
            ValueError: If the username is invalid or already exists.
        """

        get_logger().debug(f"Creating user: {username}")

        if not UserManager.is_username_valid(username):
            get_logger().debug(f"Invalid username: {username}")
            raise ValueError(f"Invalid username: {username}")

        if UserManager.username_exists(username):
            get_logger().debug(f"User '{username}' already exists.")
            raise UserAlreadyExistsException(f"User '{username}' already exists.")

        user = DBClient.create_user(username)
        DockerNetworkManager.create_network(username)

        get_logger().info(f"User '{username}' created successfully.")

        return user

    @staticmethod
    def get_by_name(username: str) -> User:
        """
        Retrieves a user by their username.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object if found, otherwise raises an exception.
        """

        user = DBClient.get_user_by_name(username)
        if not user:
            raise UserNotFoundException(f"User '{username}' not found.")

        return user
