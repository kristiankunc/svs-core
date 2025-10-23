from enum import Enum
from pathlib import Path
from types import MappingProxyType

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class EnvManager:
    """Manages reading and caching environment variables from a .env file."""

    ENV_FILE_PATH = Path("/etc/svs/.env")
    DEV_ENV_FILE_PATH = Path(".env")

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
        """Get the current runtime environment from the .env file.

        Returns:
            EnvManager.RuntimeEnvironment: The current runtime environment. Defaults to PRODUCTION if not set.
        """

        if not cls._env_loaded or cls._env_cache_internal is None:
            cls._read_env()

        assert cls._env_cache_internal is not None
        env_value = cls._env_cache_internal.get(
            "RUNTIME_ENVIRONMENT", cls.RuntimeEnvironment.PRODUCTION.value
        ).lower()

        try:
            return cls.RuntimeEnvironment(env_value)
        except ValueError:
            return cls.RuntimeEnvironment.PRODUCTION

    @classmethod
    def get_database_url(cls) -> str | None:
        """Get the DATABASE_URL from the .env file.

        Returns:
            str | None: The database URL if set, otherwise None.
        """

        if not cls._env_loaded or cls._env_cache is None:
            cls._read_env()

        assert cls._env_cache is not None
        return cls._env_cache.get("DATABASE_URL")

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

        # TODO: fix docs

        res = run_command(f"cat {path.as_posix()}")

        for line in res.stdout.splitlines():
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value

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
                get_logger(__name__, independent=True).info(
                    f"Loaded .env from {cls.ENV_FILE_PATH}"
                )
            except FileNotFoundError as e:
                get_logger(__name__, independent=True).error(
                    f"{cls.ENV_FILE_PATH} not found."
                )
                raise e

            cls._env_cache_internal = env_vars
            cls._env_cache = MappingProxyType(env_vars)

            if cls.get_runtime_environment() == cls.RuntimeEnvironment.DEVELOPMENT:
                get_logger(__name__, independent=True).info(
                    "Running in DEVELOPMENT environment as per .env configuration, loading local .env"
                )

                try:
                    local_env_vars = cls._open_env_file(cls.DEV_ENV_FILE_PATH)
                    cls._env_cache_internal.update(local_env_vars)
                    cls._env_cache = MappingProxyType(cls._env_cache_internal)
                    get_logger(__name__, independent=True).info(
                        f"Loaded local .env from {cls.DEV_ENV_FILE_PATH}"
                    )
                except FileNotFoundError:
                    get_logger(__name__, independent=True).warning(
                        f"Local .env file {cls.DEV_ENV_FILE_PATH} not found."
                    )

        cls._env_loaded = True
        return cls._env_cache
