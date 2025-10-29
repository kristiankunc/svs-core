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

    @classmethod
    def from_dict(cls, key: str, value: str) -> "KeyValue":
        """Creates a KeyValue instance from a key-value pair.

        Args:
            key (str): The key of the pair.
            value (str): The value of the pair.

        Returns:
            KeyValue: A new KeyValue instance.
        """
        return cls(key=key, value=value)

    def to_dict(self) -> dict[str, str]:
        """Converts the KeyValue instance to a dictionary.

        Returns:
            dict[str, str]: A dictionary representation of the key-value pair.
        """
        return {self.key: self.value}

    def __str__(self) -> str:
        """Returns a string representation of the KeyValue instance.

        Returns:
            str: A string in the format 'key=value'.
        """
        return f"{self.key}={self.value}"


class EnvVariable(KeyValue):  # noqa: D101
    """Environment variable represented as a key-value pair."""

    @classmethod
    def from_dict(cls, key: str, value: str) -> "EnvVariable":
        """Creates an EnvVariable instance from a key-value pair.

        Args:
            key (str): The key of the pair.
            value (str): The value of the pair.

        Returns:
            EnvVariable: A new EnvVariable instance.
        """
        return cls(key=key, value=value)


class Label(KeyValue):  # noqa: D101
    """Docker label represented as a key-value pair."""

    @classmethod
    def from_dict(cls, key: str, value: str) -> "Label":
        """Creates a Label instance from a key-value pair.

        Args:
            key (str): The key of the pair.
            value (str): The value of the pair.

        Returns:
            Label: A new Label instance.
        """
        return cls(key=key, value=value)


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

    @classmethod
    def from_dict(cls, port_dict: dict[str, int | None]) -> "ExposedPort":
        """Creates an ExposedPort instance from a dictionary.

        Args:
            port_dict (dict[str, int | None]): A dictionary containing 'container' and optionally 'host' keys.

        Returns:
            ExposedPort: A new ExposedPort instance.

        Raises:
            ValueError: If 'container' key is missing or invalid.
        """
        if "container" not in port_dict:
            raise ValueError(
                f"Port specification must contain a 'container' field: {port_dict}"
            )

        container_port = port_dict.get("container")
        if not isinstance(container_port, int):
            raise ValueError(f"Container port must be an integer: {port_dict}")

        host_port = port_dict.get("host")
        return cls(
            container_port=container_port,
            host_port=host_port if isinstance(host_port, int) else None,
        )

    def to_dict(self) -> dict[str, int | None]:
        """Converts the ExposedPort instance to a dictionary.

        Returns:
            dict[str, int | None]: A dictionary representation of the port mapping.
        """
        result: dict[str, int | None] = {"container": self.container_port}
        result["host"] = self.host_port
        return result

    def __str__(self) -> str:
        """Returns a string representation of the ExposedPort instance.

        Returns:
            str: A string in the format 'host_port:container_port' or 'container_port' if host_port is None.
        """
        if self.host_port is not None:
            return f"{self.host_port}:{self.container_port}"
        return f"{self.container_port}"


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

    @classmethod
    def from_dict(cls, volume_dict: dict[str, str | None]) -> "Volume":
        """Creates a Volume instance from a dictionary.

        Args:
            volume_dict (dict[str, str | None]): A dictionary containing 'container' and optionally 'host' keys.

        Returns:
            Volume: A new Volume instance.

        Raises:
            ValueError: If 'container' key is missing or invalid.
        """
        if "container" not in volume_dict:
            raise ValueError(
                f"Volume specification must contain a 'container' field: {volume_dict}"
            )

        container_path = volume_dict.get("container")
        if not isinstance(container_path, str):
            raise ValueError(f"Container path must be a string: {volume_dict}")

        host_path = volume_dict.get("host")
        if host_path is not None and not isinstance(host_path, str):
            raise ValueError(
                f"Host path must be a string or None if specified: {volume_dict}"
            )

        return cls(
            container_path=str(container_path),
            host_path=str(host_path) if host_path is not None else None,
        )

    def to_dict(self) -> dict[str, str | None]:
        """Converts the Volume instance to a dictionary.

        Returns:
            dict[str, str | None]: A dictionary representation of the volume mapping.
        """
        result: dict[str, str | None] = {"container": self.container_path}
        result["host"] = self.host_path
        return result

    def __str__(self) -> str:
        """Returns a string representation of the Volume instance.

        Returns:
            str: A string in the format 'host_path:container_path' or 'container_path' if host_path is None.
        """
        if self.host_path is not None:
            return f"{self.host_path}:{self.container_path}"
        return f"{self.container_path}"


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

    @classmethod
    def from_dict(
        cls, healthcheck_dict: dict[str, str | list[str] | int | None]
    ) -> "Healthcheck | None":
        """Creates a Healthcheck instance from a dictionary.

        Args:
            healthcheck_dict (dict[str, str | list[str] | int | None]): A dictionary containing healthcheck configuration.

        Returns:
            Healthcheck | None: A new Healthcheck instance, or None if the dictionary is empty.

        Raises:
            ValueError: If 'test' key is missing.
        """
        if not healthcheck_dict or "test" not in healthcheck_dict:
            return None

        test_value = healthcheck_dict.get("test", [])
        test_list: list[str] = test_value if isinstance(test_value, list) else []

        interval_value = healthcheck_dict.get("interval")
        interval: str | None = (
            str(interval_value) if isinstance(interval_value, (str, int)) else None
        )

        timeout_value = healthcheck_dict.get("timeout")
        timeout: str | None = (
            str(timeout_value) if isinstance(timeout_value, (str, int)) else None
        )

        retries_value = healthcheck_dict.get("retries")
        retries: int | None = retries_value if isinstance(retries_value, int) else None

        start_period_value = healthcheck_dict.get("start_period")
        start_period: str | None = (
            str(start_period_value)
            if isinstance(start_period_value, (str, int))
            else None
        )

        return cls(
            test=test_list,
            interval=interval,
            timeout=timeout,
            retries=retries,
            start_period=start_period,
        )

    def to_dict(self) -> dict[str, str | list[str] | int]:
        """Converts the Healthcheck instance to a dictionary.

        Returns:
            dict[str, str | list[str] | int]: A dictionary representation of the healthcheck configuration.
        """
        result: dict[str, str | list[str] | int] = {"test": self.test}
        if self.interval is not None:
            result["interval"] = int(self.interval)
        if self.timeout is not None:
            result["timeout"] = int(self.timeout)
        if self.retries is not None:
            result["retries"] = self.retries
        if self.start_period is not None:
            result["start_period"] = int(self.start_period)
        return result

    def __str__(self) -> str:
        """Returns a string representation of the Healthcheck instance.

        Returns:
            str: A string representation of the healthcheck configuration.
        """
        parts = [f"test={self.test}"]
        if self.interval is not None:
            parts.append(f"interval={self.interval}")
        if self.timeout is not None:
            parts.append(f"timeout={self.timeout}")
        if self.retries is not None:
            parts.append(f"retries={self.retries}")
        if self.start_period is not None:
            parts.append(f"start_period={self.start_period}")
        return "Healthcheck(" + ", ".join(parts) + ")"
