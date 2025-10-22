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
            "RUNTIME_ENVIRONMENT", "development"
        ).lower()

        try:
            return cls.RuntimeEnvironment(env_value)
        except ValueError:
            get_logger(__name__).warning(
                f"Unknown environment '{env_value}', defaulting to DEVELOPMENT."
            )
            return cls.RuntimeEnvironment.DEVELOPMENT

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
                with open(cls.ENV_FILE_PATH, "r") as env_file:
                    for line in env_file:
                        if line.strip() and not line.startswith("#"):
                            key, value = line.strip().split("=", 1)
                            env_vars[key] = value

            except FileNotFoundError as e:
                get_logger(__name__).error(f"{cls.ENV_FILE_PATH} not found.")
                raise e

            cls._env_cache_internal = env_vars
            cls._env_cache = MappingProxyType(env_vars)

        cls._env_loaded = True
        return cls._env_cache
