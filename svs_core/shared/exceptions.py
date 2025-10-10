class SVSException(Exception):
    """Base class for all SVS exceptions."""

    pass


class AlreadyExistsException(SVSException):
    """Exception raised when an entity already exists."""

    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} with identifier '{identifier}' already exists.")
        self.entity = entity
        self.identifier = identifier


class NotFoundException(SVSException):
    """Exception raised when an item is not found."""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidOperationException(SVSException):
    """Exception raised when an operation is invalid."""

    def __init__(self, message: str):
        super().__init__(message)
