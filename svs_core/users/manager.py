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
    
    def __init__(self):
        super().__init__()

    def _is_username_valid(self, username: str) -> bool:
        """
        Validates the username against a regex pattern.
        
        Args:
            username (str): The username to validate.
        
        Returns:
            bool: True if the username is valid, False otherwise.
        """
        username_regex = r"^[a-z_][a-z0-9_-]{0,30}[a-z0-9_]$"
        return bool(re.match(username_regex, username))

    def _user_exists(self, username: str) -> bool:
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

        if not self._is_username_valid(name):
            self.logger.error(f"Invalid username: {name}")
            raise ValueError(f"Invalid username: {name}")

        if self._user_exists(name):
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

        if not self._user_exists(name):
            self.logger.error(f"User {name} does not exist.")
            raise ValueError(f"User {name} does not exist.")

        self.execute(f"sudo userdel {name}")
        self.logger.info(f"User {name} deleted successfully.")