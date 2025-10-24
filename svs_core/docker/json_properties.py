# TODO: possibly document


class KeyValue:  # noqa: D101
    """Generic key-value pair class."""

    def __init__(self, key: str, value: str):
        """Initializes a KeyValue instance.

        Args:
            key (str): The key of the pair.
            value (str): The value of the pair.
        """

        self.key = key
        self.value = value


class EnvVariable(KeyValue):  # noqa: D101
    """Environment variable represented as a key-value pair."""

    pass


class Label(KeyValue):  # noqa: D101
    """Docker label represented as a key-value pair."""

    pass


class ExposedPort:  # noqa: D101
    """Represents a port exposed by a Docker container."""

    def __init__(self, container_port: int, host_port: int | None = None):
        """Initializes an ExposedPort instance.

        Args:
            container_port (int): The port inside the container.
            host_port (int | None): The port on the host machine. If None, a random port will be assigned.
        """

        self.container_port = container_port
        self.host_port = host_port


class Volume:  # noqa: D101
    """Represents a volume mapping for a Docker container."""

    def __init__(self, container_path: str, host_path: str | None = None):
        """Initializes a Volume instance.

        Args:
            container_path (str): The path inside the container.
            host_path (str | None): The path on the host machine. If None, a Docker-managed volume will be used.
        """

        self.container_path = container_path
        self.host_path = host_path


class Healthcheck:  # noqa: D101
    """Represents a healthcheck configuration for a Docker container."""

    def __init__(
        self,
        test: list[str],
        interval: str | None = None,
        timeout: str | None = None,
        retries: int | None = None,
        start_period: str | None = None,
    ):
        """Initializes a Healthcheck instance.

        Args:
            test (list[str]): The command to run to check the health of the container.
            interval (str | None): The time between running the check. Defaults to None.
            timeout (str | None): The time to wait before considering the check to have failed. Defaults to None.
            retries (int | None): The number of consecutive failures needed to consider the container unhealthy. Defaults to None.
            start_period (str | None): The initialization time before starting health checks. Defaults to None.
        """

        self.test = test
        self.interval = interval
        self.timeout = timeout
        self.retries = retries
        self.start_period = start_period
