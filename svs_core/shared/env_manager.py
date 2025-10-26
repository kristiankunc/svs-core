from __future__ import annotations

import logging
import os
import subprocess

from enum import Enum
from pathlib import Path
from types import MappingProxyType

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class EnvManager:
    """Manages reading and caching environment variables from a .env file."""

    ENV_FILE_PATH = Path("/etc/svs/.env")

    _env_loaded: bool = False
    _env_vars: dict[str, str] = {}

    class EnvVarKeys(Enum):
        """Enumeration of environment variable keys."""

        RUNTIME_ENVIRONMENT = "ENVIRONMENT"
        DATABASE_URL = "DATABASE_URL"

    class RuntimeEnvironment(Enum):
        """Enumeration of possible runtime environments."""

        PRODUCTION = "production"
        DEVELOPMENT = "development"
        TESTING = "testing"

    @classmethod
    def _get(cls, value: EnvManager.EnvVarKeys) -> str | None:
        """Get the value of an environment variable by its key.

        Args:
            value (EnvManager.EnvVarKeys): The key of the environment variable.

        Returns:
            str | None: The value of the environment variable if set, otherwise None.
        """

        if not cls._env_loaded:
            cls._load_env()

        return cls._env_vars.get(value.value)

    @classmethod
    def get_runtime_environment(cls) -> EnvManager.RuntimeEnvironment:
        """Get the current runtime environment from the .env file.

        Returns:
            EnvManager.RuntimeEnvironment: The current runtime environment. Defaults to PRODUCTION if not set.
        """

        value = cls._get(cls.EnvVarKeys.RUNTIME_ENVIRONMENT)
        return EnvManager.RuntimeEnvironment(
            value or cls.RuntimeEnvironment.PRODUCTION.value
        )

    @classmethod
    def get_database_url(cls) -> str | None:
        """Get the DATABASE_URL from the .env file.

        Returns:
            str | None: The database URL if set, otherwise None.
        """

        return cls._get(cls.EnvVarKeys.DATABASE_URL)

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
            res = run_command(
                f"cat {path.as_posix()}", logger=get_logger(__name__, independent=True)
            )
        except subprocess.CalledProcessError:
            raise FileNotFoundError(f"Environment file not found: {path.as_posix()}")

        if res is None:
            return env_vars

        for line in res.stdout.splitlines():
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                env_vars[key] = value

        return env_vars

    @classmethod
    def _load_env(cls) -> None:
        """Reads the .env file and caches environment variables."""

        try:
            loaded_vars = cls._open_env_file(cls.ENV_FILE_PATH)
            # os.environ vars override .env file vars so we merge them with os.environ last
            merged_vars = {**loaded_vars, **os.environ}
            cls._env_vars = merged_vars
            cls._env_loaded = True
        except FileNotFoundError:
            get_logger(__name__, independent=True).warning(
                f".env file not found at {cls.ENV_FILE_PATH.as_posix()}. Using defaults."
            )
            cls._env_loaded = True
