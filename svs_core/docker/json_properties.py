import os

from typing import Self

from pydantic import BaseModel, Field, field_validator

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import create_directory, run_command


class EnvVariable(BaseModel):
    """Environment variable represented as a key-value pair.

    Attributes:
        key: Environment variable name.
        value: Environment variable value.
    """

    key: str = Field(min_length=1)
    value: str

    def __str__(self) -> str:
        return f"EnvVariable({self.key}={self.value})"

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        """Creates an EnvVariable instance from a dictionary.

        Args:
            data (dict[str, str]): A dictionary with "key" and "value" fields.

        Returns:
            Self: A new EnvVariable instance.

        Raises:
            ValueError: If required fields are missing.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("Dictionary must contain 'key' and 'value' fields")
        return cls(key=data["key"], value=data["value"])

    @classmethod
    def from_dict_array(cls, data: list[dict[str, str]]) -> list[Self]:
        """Creates a list of EnvVariable instances from a list of dictionaries.

        Args:
            data (list[dict[str, str]]): A list of dictionaries.

        Returns:
            list[Self]: A list of EnvVariable instances.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def to_dict_array(items: list["EnvVariable"]) -> list[dict[str, str]]:
        """Converts a list of EnvVariable instances to a list of dictionaries.

        Args:
            items (list[EnvVariable]): A list of EnvVariable instances.

        Returns:
            list[dict[str, str]]: A list of dictionaries.
        """
        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict[str, str]:
        """Converts the EnvVariable instance to a dictionary.

        Returns:
            dict[str, str]: A dictionary with "key" and "value" fields.
        """
        return {"key": self.key, "value": self.value}


class Label(BaseModel):
    """Docker label represented as a key-value pair.

    Attributes:
        key: Label name.
        value: Label value.
    """

    key: str = Field(min_length=1)
    value: str

    def __str__(self) -> str:
        return f"Label({self.key}={self.value})"

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        """Creates a Label instance from a dictionary.

        Args:
            data (dict[str, str]): A dictionary with "key" and "value" fields.

        Returns:
            Self: A new Label instance.

        Raises:
            ValueError: If required fields are missing.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("Dictionary must contain 'key' and 'value' fields")
        return cls(key=data["key"], value=data["value"])

    @classmethod
    def from_dict_array(cls, data: list[dict[str, str]]) -> list[Self]:
        """Creates a list of Label instances from a list of dictionaries.

        Args:
            data (list[dict[str, str]]): A list of dictionaries.

        Returns:
            list[Self]: A list of Label instances.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def to_dict_array(items: list["Label"]) -> list[dict[str, str]]:
        """Converts a list of Label instances to a list of dictionaries.

        Args:
            items (list[Label]): A list of Label instances.

        Returns:
            list[dict[str, str]]: A list of dictionaries.
        """
        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict[str, str]:
        """Converts the Label instance to a dictionary.

        Returns:
            dict[str, str]: A dictionary with "key" and "value" fields.
        """
        return {"key": self.key, "value": self.value}


class ExposedPort(BaseModel):
    """Represents an exposed port for a Docker container.

    Binds host_port → container_port.

    Serialization uses {"key": host_port, "value": container_port} for
    backward compatibility with Django JSON field storage.

    Attributes:
        host_port: Port on the host machine (optional, None for dynamic assignment).
        container_port: Port inside the Docker container (mandatory).
    """

    host_port: int | None = None
    container_port: int = Field(gt=0)

    def __str__(self) -> str:
        return f"ExposedPort({self.host_port}->{self.container_port})"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Creates an ExposedPort instance from a dictionary.

        Args:
            data (dict): A dictionary with "key" (host_port) and "value" (container_port) fields.

        Returns:
            Self: A new ExposedPort instance.
        """
        return cls(
            host_port=data.get("key"),
            container_port=data["value"],
        )

    @classmethod
    def from_dict_array(cls, data: list[dict]) -> list[Self]:
        """Creates a list of ExposedPort instances from a list of dictionaries.

        Args:
            data (list[dict]): A list of dictionaries.

        Returns:
            list[Self]: A list of ExposedPort instances.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def to_dict_array(items: list["ExposedPort"]) -> list[dict]:
        """Converts a list of ExposedPort instances to a list of dictionaries.

        Args:
            items (list[ExposedPort]): A list of ExposedPort instances.

        Returns:
            list[dict]: A list of dicts with "key" and "value" fields.
        """
        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict:
        """Converts the ExposedPort instance to a dictionary.

        Returns:
            dict: A dictionary with "key" (host_port) and "value" (container_port).
        """
        return {"key": self.host_port, "value": self.container_port}


class Volume(BaseModel):
    """Represents a volume for a Docker container.

    Binds host_path → container_path.

    Serialization uses {"key": host_path, "value": container_path} for
    backward compatibility with Django JSON field storage.

    Attributes:
        host_path: Path on the host machine (optional, None for anonymous volumes).
        container_path: Path inside the Docker container (mandatory).
    """

    host_path: str | None = None
    container_path: str = Field(min_length=1)

    def __str__(self) -> str:
        return f"Volume({self.container_path}={self.host_path})"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Creates a Volume instance from a dictionary.

        Args:
            data (dict): A dictionary with "key" (host_path) and "value" (container_path) fields.

        Returns:
            Self: A new Volume instance.
        """
        return cls(
            host_path=data.get("key"),
            container_path=data["value"],
        )

    @classmethod
    def from_dict_array(cls, data: list[dict]) -> list[Self]:
        """Creates a list of Volume instances from a list of dictionaries.

        Args:
            data (list[dict]): A list of dictionaries.

        Returns:
            list[Self]: A list of Volume instances.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def to_dict_array(items: list["Volume"]) -> list[dict]:
        """Converts a list of Volume instances to a list of dictionaries.

        Args:
            items (list[Volume]): A list of Volume instances.

        Returns:
            list[dict]: A list of dicts with "key" and "value" fields.
        """
        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict:
        """Converts the Volume instance to a dictionary.

        Returns:
            dict: A dictionary with "key" (host_path) and "value" (container_path).
        """
        return {"key": self.host_path, "value": self.container_path}


class DefaultContent(BaseModel):
    """Represents a default content file for a Docker template.

    Serialization uses {"key": location, "value": content} for
    backward compatibility with Django JSON field storage.

    Attributes:
        location: File path inside the container.
        content: Content of the file.
    """

    location: str = Field(min_length=1)
    content: str

    def __str__(self) -> str:
        content_preview = (
            self.content[:50] + "..." if len(self.content) > 50 else self.content
        )
        return f"DefaultContent({self.location}={content_preview})"

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        """Creates a DefaultContent instance from a dictionary.

        Args:
            data (dict): A dictionary with "key" (location) and "value" (content) fields.

        Returns:
            Self: A new DefaultContent instance.
        """
        if "key" not in data or "value" not in data:
            raise ValueError("Dictionary must contain 'key' and 'value' fields")
        return cls(location=data["key"], content=data["value"])

    @classmethod
    def from_dict_array(cls, data: list[dict]) -> list[Self]:
        """Creates a list of DefaultContent instances from a list of
        dictionaries.

        Args:
            data (list[dict]): A list of dictionaries.

        Returns:
            list[Self]: A list of DefaultContent instances.
        """
        return [cls.from_dict(item) for item in data]

    @staticmethod
    def to_dict_array(items: list["DefaultContent"]) -> list[dict]:
        """Converts a list of DefaultContent instances to a list of
        dictionaries.

        Args:
            items (list[DefaultContent]): A list of DefaultContent instances.

        Returns:
            list[dict]: A list of dicts with "key" and "value" fields.
        """
        return [item.to_dict() for item in items or []]

    def to_dict(self) -> dict:
        """Converts the DefaultContent instance to a dictionary.

        Returns:
            dict: A dictionary with "key" (location) and "value" (content).
        """
        return {"key": self.location, "value": self.content}

    def write_to_host(self, host_path: str, username: str) -> None:
        """Writes the default content to a specified path on the host.

        Args:
            host_path (str): The path on the host where the content should be written.
            username (str): The username to use for file ownership and permissions.
        """
        create_directory(os.path.dirname(host_path), user=username)
        run_command(f"echo '{self.content}' > {host_path}", check=True, user=username)


class Healthcheck(BaseModel):
    """Represents a healthcheck configuration for a Docker container.

    Attributes:
        test: Command to run to check the health of the container.
        interval: Time between running the check (in seconds).
        timeout: Time to wait before considering the check failed (in seconds).
        retries: Number of consecutive failures needed to consider unhealthy.
        start_period: Initialization time before starting health checks (in seconds).
    """

    test: list[str] | str
    interval: int | None = None
    timeout: int | None = None
    retries: int | None = None
    start_period: int | None = None

    @field_validator("test", mode="before")
    @classmethod
    def _string_to_cmd_shell(cls, v: object) -> object:
        """Convert a string test to CMD-SHELL format."""
        if isinstance(v, str):
            return ["CMD-SHELL", v]
        return v

    @field_validator("test", mode="after")
    @classmethod
    def _validate_test_list(cls, v: list[str] | str) -> list[str] | str:
        """Validate that test list items are all strings."""
        if isinstance(v, list) and not all(isinstance(cmd, str) for cmd in v):
            raise ValueError("'test' must be a list of strings or a string")
        return v

    class HealthStatus:
        """Represents the health status of a container."""

        HEALTHY = "healthy"
        UNHEALTHY = "unhealthy"
        STARTING = "starting"

        @staticmethod
        def from_str(status: str) -> str | None:
            """Converts a string to a HealthStatus enum value.

            Args:
                status (str | None): The health status as a string.

            Returns:
                str: The corresponding health status string.

            Raises:
                ValueError: If the input string does not match any valid health status.
            """
            status = status.lower()
            if status == "healthy":
                return Healthcheck.HealthStatus.HEALTHY
            elif status == "unhealthy":
                return Healthcheck.HealthStatus.UNHEALTHY
            elif status == "starting":
                return Healthcheck.HealthStatus.STARTING
            elif status == "unknown":
                return None
            else:
                get_logger(__name__).error(f"Invalid health status: {status}")
                raise ValueError(
                    f"Invalid health status: {status}. Expected 'healthy', 'unhealthy', or 'starting'."
                )

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
            ValueError: If 'test' key is missing.
        """
        if not healthcheck_dict:
            return None
        if "test" not in healthcheck_dict:
            raise ValueError("'test' key is required in healthcheck_dict")
        return cls.model_validate(healthcheck_dict)

    def to_dict(self) -> dict[str, str | list[str] | int | None]:
        """Converts the Healthcheck instance to a dictionary.

        Returns:
            dict[str, str | list[str] | int | None]: A dictionary representation of the healthcheck configuration.
        """
        return self.model_dump(exclude_none=True)  # type: ignore[return-value]

    def to_docker_api_format(self) -> dict[str, list[str] | int | None]:
        """Converts the Healthcheck instance to Docker API format.

        The Docker API expects times in nanoseconds (seconds * 10^9).

        Returns:
            dict[str, list[str] | int | None]: A dictionary with Docker API format.
                Keys are: Test, Interval, Timeout, Retries, StartPeriod.
        """
        result: dict[str, list[str] | int | None] = {"Test": self.test}

        # Convert seconds to nanoseconds for Docker API
        if self.interval is not None:
            result["Interval"] = int(self.interval * 1_000_000_000)
        if self.timeout is not None:
            result["Timeout"] = int(self.timeout * 1_000_000_000)
        if self.retries is not None:
            result["Retries"] = self.retries
        if self.start_period is not None:
            result["StartPeriod"] = int(self.start_period * 1_000_000_000)

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
