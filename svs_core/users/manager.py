import re
from svs_core.shared.shell import run_command
from svs_core.db.client import get_db_session
from svs_core.db.models import User
from svs_core.event_adapters.base import Dispatcher
from svs_core.event_adapters.base import Event


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

        if not re.match(r'^[a-z_][a-z0-9_-]*[$]?$', username):
            return False

        if username.endswith('-'):
            return False

        return True

    @staticmethod
    def name_exists_in_system(username: str) -> bool:
        """Checks if the user exists in the system.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            result = run_command(f"id -u {username}", check=False)
            return result.returncode == 0
        except Exception:
            return False

    @staticmethod
    def name_exists_in_db(username: str) -> bool:
        """Checks if the user exists in the database.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        with get_db_session() as session:
            user = session.query(User).filter_by(name=username).first()
            return user is not None

    @staticmethod
    def create_user(username: str) -> None:
        if not UserManager.is_username_valid(username):
            raise ValueError(f"Invalid username: {username}")

        if UserManager.name_exists_in_system(
                username) or UserManager.name_exists_in_db(username):
            raise ValueError(f"User {username} already exists in system or database.")

        Dispatcher.dispatch(Event.CREATE_USER, username=username)

    @staticmethod
    def delete_user(username: str) -> None:
        if not UserManager.is_username_valid(username):
            raise ValueError(f"Invalid username: {username}")

        if not UserManager.name_exists_in_system(
                username) and not UserManager.name_exists_in_db(username):
            raise ValueError(f"User {username} does not exist in system or database.")

        Dispatcher.dispatch(Event.DELETE_USER, username=username)
