from __future__ import annotations

import re

from typing import cast

from svs_core.db.models import UserModel
from svs_core.docker.network import DockerNetworkManager
from svs_core.shared.exceptions import (
    AlreadyExistsException,
    InvalidOperationException,
    SVSException,
)
from svs_core.shared.hash import hash_password
from svs_core.shared.logger import get_logger
from svs_core.shared.volumes import SystemVolumeManager
from svs_core.users.system import SystemUserManager


class InvalidUsernameException(SVSException):
    """Exception raised when the provided username is invalid.

    When created, a system users and a docker network will be created
    holding the same name.
    """

    def __init__(self, username: str):
        super().__init__(f"Invalid username: '{username}'.")
        self.username = username


class InvalidPasswordException(SVSException):
    """Exception raised when the provided password is invalid."""

    def __init__(self, password: str):
        super().__init__(
            f"Invalid password: '{password}'. Password must be at least 8 characters long."
        )
        self.password = password


class User(UserModel):
    """User class representing a user in the system."""

    class Meta:  # noqa: D106
        proxy = True

    @classmethod
    def create(cls, name: str, password: str, is_admin: bool = False) -> User:
        """Creates a new user with the given name and password.

        Args:
            name (str): The username for the new user.
            password (str): The password for the new user.
            is_admin (bool): Whether the user should be admin.

        Raises:
            AlreadyExistsException: If the username already exists.
            InvalidUsernameException: If the username is invalid.

        Returns:
            User: The created user instance.
        """
        if not cls.is_username_valid(name):
            raise InvalidUsernameException(name)
        if not cls.is_password_valid(password):
            raise InvalidPasswordException(password)
        if cls.username_exists(name):
            raise AlreadyExistsException(entity="User", identifier=name)

        user: "User" = cls.objects.create(
            name=name, password=hash_password(password).decode("utf-8")
        )

        DockerNetworkManager.create_network(name, labels={"svs_user": name})
        SystemUserManager.create_user(name, password, is_admin)

        get_logger(__name__).info(f"Created user: {name}")
        return user

    @staticmethod
    def is_username_valid(username: str) -> bool:
        """Validates the username based on specific criteria.

        The username needs to be a valid UNIX username.

        Args:
            username (str): The username to validate.

        Returns:
            bool: True if the username is valid, False otherwise.
        """
        if not isinstance(username, str):
            return False
        if len(username) == 0 or len(username) > 32:
            return False

        pattern = r"^[a-z_][a-z0-9_-]{0,30}\$?$"
        return bool(re.match(pattern, username))

    @staticmethod
    def is_password_valid(password: str) -> bool:
        """Validates the password based on specific criteria.

        The password must be at least 8 characters long.

        Args:
            password (str): The password to validate.

        Returns:
            bool: True if the password is valid, False otherwise.
        """
        return isinstance(password, str) and len(password) >= 8

    @classmethod
    def username_exists(cls, username: str) -> bool:
        """Checks if a username already exists in the database.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        return cast(bool, cls.objects.filter(name=username).exists())

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the user's password.

        Args:
            password (str): The password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        from svs_core.shared.hash import check_password

        hashed = self.password.encode("utf-8")

        return check_password(password, hashed)

    def delete(self) -> None:
        """Deletes the user from the database and removes associated resources.

        This includes deleting the system user and Docker network
        associated with the user.
        """
        get_logger(__name__).info(f"Deleting user '{self.name}'")

        if len(self.services.all()) > 0:
            get_logger(__name__).warning(
                f"Cannot delete user '{self.name}' - has {len(self.services.all())} associated services"
            )
            raise InvalidOperationException(
                f"Cannot delete user '{self.name}' because they have associated services."
            )

        try:
            SystemVolumeManager.delete_user_volumes(self.id)
            DockerNetworkManager.delete_network(self.name)
            SystemUserManager.delete_user(self.name)
            super().delete()
            get_logger(__name__).info(f"Successfully deleted user '{self.name}'")
        except Exception as e:
            get_logger(__name__).error(f"Failed to delete user '{self.name}': {str(e)}")
            raise

    def is_admin(self) -> bool:
        """Checks if the user has administrative privileges.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return SystemUserManager.is_user_in_group(self.name, "svs-admins")

    def add_ssh_key(self, ssh_key: str) -> None:
        """Adds an SSH key to the user's authorized_keys file.

        Args:
            ssh_key (str): The SSH key to add.
        """
        get_logger(__name__).info(f"Adding SSH key to user '{self.name}'")

        try:
            SystemUserManager.add_ssh_key_to_user(self.name, ssh_key)
            get_logger(__name__).debug(
                f"Successfully added SSH key for user '{self.name}'"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to add SSH key for user '{self.name}': {str(e)}"
            )
            raise

    def remove_ssh_key(self, ssh_key: str) -> None:
        """Removes an SSH key from the user's authorized_keys file.

        Args:
            ssh_key (str): The SSH key to remove.
        """
        get_logger(__name__).info(f"Removing SSH key from user '{self.name}'")

        try:
            SystemUserManager.remove_ssh_key_from_user(self.name, ssh_key)
            get_logger(__name__).debug(
                f"Successfully removed SSH key for user '{self.name}'"
            )
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to remove SSH key for user '{self.name}': {str(e)}"
            )
            raise

    def __str__(self) -> str:
        return f"User(id={self.id}, name={self.name}, is_admin={self.is_admin()})"
