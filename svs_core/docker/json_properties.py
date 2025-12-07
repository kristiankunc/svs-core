import os

from typing import Generic, Self, TypeVar

from svs_core.shared.shell import create_directory, run_command

K = TypeVar("K")
V = TypeVar("V")


class KeyValue(Generic[K, V]):
    """Generic key-value pair representation."""

    def __init__(self, key: K, value: V):
        self.key = key
        self.value = value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.key}={self.value})"

    @classmethod
    def from_dict(cls, data: dict[str, K | V]) -> Self:
        """Creates a KeyValue instance from a dictionary.

        Args:
            data (dict[str, K | V]): A dictionary with "key" and "value" fields.

        Returns:
            Self: A new KeyValue instance.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("'key' and 'value' fields are required in dictionary")
        if len(data) > 2:
            raise ValueError("Expected only 'key' and 'value' fields")

        key = data["key"]
        value = data["value"]
        return cls(key, value)  # type: ignore[arg-type]

    @classmethod
    def from_dict_array(cls, data: list[dict[str, K | V]]) -> list[Self]:
        """Creates a list of KeyValue instances from a list of dictionaries.

        Args:
            data (list[dict[str, K | V]]): A list of dictionaries, each with "key" and "value" fields.

        Returns:
            list[Self]: A list of KeyValue instances.
        """
        return [cls.from_dict(item) for item in data]

    @classmethod
    def to_dict_array(cls, items: list[Self]) -> list[dict[str, K | V]]:
        """Converts a list of KeyValue instances to a list of dictionaries.

        Args:
            items (list[Self]): A list of KeyValue instances.

        Returns:
            list[dict[str, K | V]]: A list of dictionaries.
        """

        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict[str, K | V]:
        """Converts the KeyValue instance to a dictionary.

        Returns:
            dict[str, K | V]: A dictionary with "key" and "value" fields.
        """

        # type: ignore[return-value]
        return {"key": self.key, "value": self.value}


class EnvVariable(KeyValue[str, str]):
    """Environment variable represented as a key-value pair."""

    @classmethod
    # type: ignore[override]
    def from_dict(cls, data: dict[str, str]) -> "EnvVariable":
        """Creates an EnvVariable instance from a dictionary.

        Args:
            data (dict[str, str]): A dictionary with "key" and "value" fields.

        Returns:
            EnvVariable: A new EnvVariable instance.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("Dictionary must contain 'key' and 'value' fields")
        return cls(key=data["key"], value=data["value"])


class Label(KeyValue[str, str]):
    """Docker label represented as a key-value pair."""

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Label":  # type: ignore[override]
        """Creates a Label instance from a dictionary.

        Args:
            data (dict[str, str]): A dictionary with "key" and "value" fields.

        Returns:
            Label: A new Label instance.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("Dictionary must contain 'key' and 'value' fields")
        return cls(key=data["key"], value=data["value"])


class ExposedPort(KeyValue[int | None, int]):
    """Represents an exposed port for a Docker container.

    Binds: host_port=container_port

    Note: Uses key=host_port (optional) and value=container_port (mandatory) for storage.
    This ensures container_port is always present for merging operations.
    Serialization uses the format {"key": host_port, "value": container_port}.
    """

    def __init__(self, host_port: int | None, container_port: int):
        """Initializes an ExposedPort instance.

        Args:
            host_port (int | None): The port on the host machine, or None for dynamic assignment.
            container_port (int): The port inside the Docker container (mandatory).
        """

        super().__init__(key=host_port, value=container_port)

    @property
    def host_port(self) -> int | None:  # noqa: D102
        return self.key

    @host_port.setter
    def host_port(self, port: int | None) -> None:  # noqa: D102
        self.key = port

    @property
    def container_port(self) -> int:  # noqa: D102
        return self.value

    @container_port.setter
    def container_port(self, port: int) -> None:  # noqa: D102
        self.value = port


class Volume(KeyValue[str | None, str]):
    """Represents a volume for a Docker container.

    Binds: container_path=host_path

    Note: Uses key=host_path (optional) and value=container_path (mandatory) for storage.
    This ensures container_path is always present for merging operations.
    Serialization uses the format {"key": host_path, "value": container_path}.
    """

    def __init__(self, host_path: str | None, container_path: str):
        """Initializes a Volume instance.

        Args:
            host_path (str | None): The path on the host machine, or None for anonymous volumes.
            container_path (str): The path inside the Docker container (mandatory).
        """
        super().__init__(key=host_path, value=container_path)

    @property
    def host_path(self) -> str | None:  # noqa: D102
        return self.key

    @host_path.setter
    def host_path(self, path: str | None) -> None:  # noqa: D102
        self.key = path

    @property
    def container_path(self) -> str:  # noqa: D102
        return self.value

    @container_path.setter
    def container_path(self, path: str) -> None:  # noqa: D102
        self.value = path

    def __str__(self) -> str:
        """Return a string representation.

        Showing container_path=host_path format.

        Returns:
            str: A string representation of the volume.
        """

        return f"Volume({self.container_path}={self.host_path})"


class DefaultContent(KeyValue[str, str]):
    """Represents a default content file for a Docker template.

    Binds: location=content

    Note: Uses key=location and value=content for storage.
    Represents a file to be created in the container with specified content.
    Serialization uses the format {"key": location, "value": content}.
    """

    def __init__(self, location: str, content: str):
        """Initializes a DefaultContent instance.

        Args:
            location (str): The file path inside the container.
            content (str): The content of the file.
        """
        super().__init__(key=location, value=content)

    @property
    def location(self) -> str:  # noqa: D102
        return self.key

    @location.setter
    def location(self, path: str) -> None:  # noqa: D102
        self.key = path

    @property
    def content(self) -> str:  # noqa: D102
        return self.value

    @content.setter
    def content(self, text: str) -> None:  # noqa: D102
        self.value = text

    def write_to_host(self, host_path: str, username: str) -> None:
        """Writes the default content to a specified path on the host.

        Args:
            host_path (str): The path on the host where the content should be written.
            username (str): The username to use for file ownership and permissions.
        """

        create_directory(os.path.dirname(host_path))
        run_command(f"echo '{self.content}' > {host_path}", check=True, user=username)

    def __str__(self) -> str:
        """Return a string representation.

        Showing location=content format.

        Returns:
            str: A string representation of the default content.
        """
        # Truncate content for display if too long
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"DefaultContent({self.location}={content_preview})"


class Healthcheck:  # noqa: D101
    """Represents a healthcheck configuration for a Docker container."""

    def __init__(
        self,
        test: list[str],
        interval: int | None = None,
        timeout: int | None = None,
        retries: int | None = None,
        start_period: int | None = None,
    ):
        """Initializes a Healthcheck instance.

        Args:
            test (list[str]): The command to run to check the health of the container.
            interval (int | None): The time between running the check. Defaults to None.
            timeout (int | None): The time to wait before considering the check to have failed. Defaults to None.
            retries (int | None): The number of consecutive failures needed to consider the container unhealthy. Defaults to None.
            start_period (int | None): The initialization time before starting health checks. Defaults to None.
        """

        self.test = test
        self.interval = interval
        self.timeout = timeout
        self.retries = retries
        self.start_period = start_period

    @classmethod
    def from_dict(
        cls, healthcheck_dict: dict[str, str | list[str] | int | None] | None
    ) -> "Healthcheck | None":
        """Creates a Healthcheck instance from a dictionary.

        Args:
            healthcheck_dict (dict[str, str | list[str] | int | None] | None): A dictionary containing healthcheck configuration, or None.

        Returns:
            Healthcheck | None: A new Healthcheck instance, or None if the dictionary is empty or None.

        Raises:
            ValueError: If 'test' key is missing or invalid.
            TypeError: If any value has an unexpected type.
        """
        if not healthcheck_dict:
            return None

        if "test" not in healthcheck_dict:
            raise ValueError("'test' key is required in healthcheck_dict")

        test_value = healthcheck_dict.get("test")
        if not isinstance(test_value, list) or not all(
            isinstance(cmd, str) for cmd in test_value
        ):
            raise TypeError("'test' must be a list of strings")

        interval = healthcheck_dict.get("interval")
        if interval is not None and not isinstance(interval, int):
            raise TypeError("'interval' must be an integer or None")

        timeout = healthcheck_dict.get("timeout")
        if timeout is not None and not isinstance(timeout, int):
            raise TypeError("'timeout' must be an integer or None")

        retries = healthcheck_dict.get("retries")
        if retries is not None and not isinstance(retries, int):
            raise TypeError("'retries' must be an integer or None")

        start_period = healthcheck_dict.get("start_period")
        if start_period is not None and not isinstance(start_period, int):
            raise TypeError("'start_period' must be an integer or None")

        return cls(
            test=test_value,
            interval=interval,
            timeout=timeout,
            retries=retries,
            start_period=start_period,
        )

    def to_dict(self) -> dict[str, str | list[str] | int | None]:
        """Converts the Healthcheck instance to a dictionary.

        Returns:
            dict[str, str | list[str] | int | None]: A dictionary representation of the healthcheck configuration.
        """
        result: dict[str, str | list[str] | int | None] = {"test": self.test}
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
