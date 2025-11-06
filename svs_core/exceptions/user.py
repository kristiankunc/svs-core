from svs_core.exceptions.base import SVSException


class InvalidUsernameException(SVSException):
    """Exception raised when the provided username is invalid."""

    def __init__(self, username: str):
        super().__init__(f"Invalid username: '{username}'.")
        self.username = username


class InvalidPasswordException(SVSException):
    """Exception raised when the provided password is invalid."""

    def __init__(self):
        super().__init__("Invalid password provided.")
