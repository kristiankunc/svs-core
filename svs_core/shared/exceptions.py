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


class ValidationException(SVSException):
    """Exception raised when user input validation fails.

    This is a user-facing exception for invalid inputs that should be
    caught and displayed with helpful messages at the CLI level.
    """

    def __init__(self, message: str):
        super().__init__(message)


class ConfigurationException(SVSException):
    """Exception raised when configuration is invalid.

    This is a user-facing exception for configuration errors such as
    invalid template configurations or service settings.
    """

    def __init__(self, message: str):
        super().__init__(message)


class ServiceOperationException(SVSException):
    """Exception raised when a service operation fails.

    This is a user-facing exception for service lifecycle operations
    (start, stop, build, etc.) that fail.
    """

    def __init__(self, message: str):
        super().__init__(message)


class TemplateException(SVSException):
    """Exception raised when template operations fail.

    This is a user-facing exception for template-related errors such as
    import failures, invalid template structure, or missing templates.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DockerOperationException(SVSException):
    """Exception raised when Docker operations fail.

    This is a user-facing exception for Docker API failures that users
    should be aware of (image pull failures, container creation errors,
    etc.).
    """

    def __init__(self, message: str):
        super().__init__(message)


class ResourceException(SVSException):
    """Exception raised when resource allocation fails.

    This is a user-facing exception for resource allocation failures (no
    free ports, no free volumes, etc.).
    """

    def __init__(self, message: str):
        super().__init__(message)
