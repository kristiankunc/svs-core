class SVSException(Exception):
    """Base class for all SVS exceptions."""

    pass


class AlreadyExistsException(SVSException):
    """Exception raised when an entity already exists."""

    def __init__(self, entity: str, identifier: str):
        super().__init__(f"{entity} with identifier '{identifier}' already exists.")
        self.entity = entity
        self.identifier = identifier
