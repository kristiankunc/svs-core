class UserNotFoundException(Exception):
    """Exception raised when a user is not found"""

    pass


class UserAlreadyExistsException(Exception):
    """Exception raised when a user already exists"""

    pass
