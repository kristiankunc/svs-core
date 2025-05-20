from svs_core.db.models import UserModel
from svs_core.shared.shell import run_command
from svs_core.db.client import get_db_session


class UserManager:
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
            user = session.query(UserModel).filter_by(name=username).first()
            return user is not None
