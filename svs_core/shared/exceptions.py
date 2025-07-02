class SVSException(Exception):
    """Base class for all SVS exceptions."""

    pass


class NotFoundException(SVSException):
    """Exception raised when an item is not found."""

    def __init__(self, message: str):
        super().__init__(message)
