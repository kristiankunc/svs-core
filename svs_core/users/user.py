import re
from typing import Any, Optional

from svs_core.db.models import OrmBase, UserModel

from svs_core.shared.exceptions import AlreadyExistsException, SVSException
from svs_core.shared.exceptions import AlreadyExistsException, NotFoundException, SVSException
from svs_core.shared.hash import hash_password
from svs_core.shared.logger import get_logger


class InvalidUsernameException(SVSException):
    """Exception raised when the provided username is invalid."""

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


class User(OrmBase):
    """User class representing a user in the system."""

    _model_cls = UserModel

    def __init__(self, model: UserModel, **_: Any):
        super().__init__(model)
        self._model: UserModel = model

    @property
    def name(self) -> str:
        return self._model.name

    @property
    def password(self) -> str:
        return self._model.password

    @classmethod
    async def create(cls, name: str, password: str) -> "User":
        """Creates a new user with the given name and password.
        Args:
            name (str): The username for the new user.
            password (str): The password for the new user.
        Raises:
            AlreadyExistsException: If the username already exists.
            InvalidUsernameError: If the username is invalid.
        Returns:
            User: The created user instance.
        """
        name = name.lower().strip()
        password = password.strip()

        if not cls.is_username_valid(name):
            raise InvalidUsernameException(name)
        if not cls.is_password_valid(password):
            raise InvalidPasswordException(password)
        if await cls.username_exists(name):
            raise AlreadyExistsException(entity="User", identifier=name)

        model = UserModel(name=name, password=hash_password(password).decode("utf-8"))
        await model.save()
        get_logger(__name__).info(f"Created user: {name}")
        return cls(model=model)

    @classmethod
    async def delete(cls, name: str) -> None:
        """Deletes a user by name.
        Args:
            name (str): The username of the user to delete.
        Raises:
            NotFoundException: If the user with the given name does not exist.
        """
        user = await cls.get_by_name(name)
        if not user:
            raise NotFoundException(f"User with name '{name}' not found.")
        await user._model.delete()

    @classmethod
    async def get_by_name(cls, name: str) -> Optional["User"]:
        return await cls._get("name", name)

    @staticmethod
    def is_username_valid(username: str) -> bool:
        """
        Validates the username based on specific criteria.
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
        """
        Validates the password based on specific criteria.
        The password must be at least 8 characters long.

        Args:
            password (str): The password to validate.
        Returns:
            bool: True if the password is valid, False otherwise.
        """
        return isinstance(password, str) and len(password) >= 8

    @classmethod
    async def username_exists(cls, username: str) -> bool:
        """
        Checks if a username already exists in the database.

        Args:
            username (str): The username to check.
        Returns:
            bool: True if the username exists, False otherwise.
        """
        return await cls._exists("name", username)

    async def check_password(self, password: str) -> bool:
        """
        Checks if the provided password matches the user's password.

        Args:
            password (str): The password to check.
        Returns:
            bool: True if the password matches, False otherwise.
        """
        from svs_core.shared.hash import check_password

        hashed = self.password.encode("utf-8")
        return check_password(password, hashed)

    def __str__(self) -> str:
        return f"User(name={self.name}, id={self.id})"
