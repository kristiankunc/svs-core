from enum import Enum
from pathlib import Path
from types import MappingProxyType

from svs_core.shared.logger import get_logger


class EnvManager:
    """Manages reading and caching environment variables from a .env file."""

    ENV_FILE_PATH = Path("/etc/svs/.env")
    _env_cache_internal: dict[str, str] | None = None  # internal mutable
    _env_cache: MappingProxyType[str, str] | None = None  # external read-only
    _env_loaded: bool = False

    class RuntimeEnvironment(Enum):
        """Enumeration of possible runtime environments."""

        PRODUCTION = "production"
        DEVELOPMENT = "development"
        TESTING = "testing"

    @classmethod
    def get_runtime_environment(cls) -> "EnvManager.RuntimeEnvironment":
        """Get the current runtime environment from the .env file, defaulting
        to DEVELOPMENT.

        Returns:
            EnvManager.RuntimeEnvironment: The current runtime environment.
        """

        if not cls._env_loaded or cls._env_cache_internal is None:
            cls._read_env()

        assert cls._env_cache_internal is not None
        env_value = cls._env_cache_internal.get(
            "RUNTIME_ENVIRONMENT", cls.RuntimeEnvironment.DEVELOPMENT.value
        ).lower()

        try:
            return cls.RuntimeEnvironment(env_value)
        except ValueError:
            get_logger(__name__).warning(
                f"Unknown environment '{env_value}', defaulting to DEVELOPMENT."
            )
            return cls.RuntimeEnvironment.DEVELOPMENT

    @classmethod
    def _open_env_file(cls, path: Path) -> dict[str, str]:
        """Opens and reads the .env file at the specified path.

        Args:
            path (Path): The path to the .env file.

        Returns:
            dict[str, str]: A dictionary of environment variables.

        Raises:
            FileNotFoundError: If the .env file does not exist.
        """

        env_vars = {}

        try:
            with open(path, "r") as env_file:
                for line in env_file:
                    if line.strip() and not line.startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value

        except FileNotFoundError as e:
            get_logger(__name__).error(f"{path} not found.")
            raise e

        return env_vars

    @classmethod
    def _read_env(cls) -> MappingProxyType[str, str]:
        """Reads environment variables from the .env file and caches them.

        Returns:
            MappingProxyType[str, str]: A read-only mapping of environment variables.

        Raises:
            FileNotFoundError: If the .env file does not exist.
        """

        if cls._env_cache is None:
            env_vars = {}

            try:
                env_vars = cls._open_env_file(cls.ENV_FILE_PATH)
            except FileNotFoundError as e:
                get_logger(__name__).error(f"{cls.ENV_FILE_PATH} not found.")
                raise e

            cls._env_cache_internal = env_vars
            cls._env_cache = MappingProxyType(env_vars)

            if cls.get_runtime_environment() == cls.RuntimeEnvironment.DEVELOPMENT:
                get_logger(__name__).info(
                    "Running in DEVELOPMENT environment as per .env configuration, loading local .env"
                )

                local_env_path = Path(".env")

                try:
                    local_env_vars = cls._open_env_file(local_env_path)
                    cls._env_cache_internal.update(local_env_vars)
                    cls._env_cache = MappingProxyType(cls._env_cache_internal)
                except FileNotFoundError:
                    get_logger(__name__).warning(
                        f"Local .env file {local_env_path} not found."
                    )

        cls._env_loaded = True
        return cls._env_cache
