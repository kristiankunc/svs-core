from __future__ import annotations

import logging
import os
import subprocess

from enum import Enum
from pathlib import Path
from types import MappingProxyType

from svs_core.shared.shell import read_file, run_command


class EnvManager:
    """Manages reading and caching environment variables from a .env file."""

    ENV_FILE_PATH = Path("/etc/svs/.env")

    class RuntimeEnvironment(Enum):
        """Enumeration of runtime environments."""

        DEVELOPMENT = "development"
        PRODUCTION = "production"
        TESTING = "testing"

    class EnvVariables(Enum):
        """Enumeration of environment variable keys."""

        ENVIRONMENT = "ENVIRONMENT"
        DATABASE_URL = "DATABASE_URL"

    @staticmethod
    def load_env_file() -> None:
        """Loads environment variables from the .env file.

        System and provided environment variables take precedence over .env file values.

        Raises:
            FileNotFoundError: If the .env file does not exist.
        """
        from svs_core.shared.logger import get_logger

        if (
            EnvManager.get_runtime_environment()
            == EnvManager.RuntimeEnvironment.DEVELOPMENT
        ):
            get_logger(__name__).debug(
                "Skipping .env loading in development environment."
            )
            return

        if not EnvManager.ENV_FILE_PATH.exists():
            get_logger(__name__).warning(
                f".env file not found at {EnvManager.ENV_FILE_PATH}"
            )
            raise FileNotFoundError(
                f".env file not found at {EnvManager.ENV_FILE_PATH}"
            )

        content = read_file(EnvManager.ENV_FILE_PATH)
        for line in content.splitlines():
            if line.strip() and not line.startswith("#"):
                key, _, value = line.partition("=")
                key_stripped = key.strip()
                if key_stripped not in os.environ:
                    os.environ[key_stripped] = value.strip().replace('"', "")

    @staticmethod
    def _get(key: EnvVariables) -> str | None:
        """Retrieves the value of the specified environment variable.

        Args:
            key (EnvVariables): The environment variable key.

        Returns:
            str | None: The value of the environment variable, or None if not set.
        """

        return os.getenv(key.value)

    @staticmethod
    def get_runtime_environment() -> EnvManager.RuntimeEnvironment:
        """Determines the current runtime environment.

        Returns:
            EnvManager.RuntimeEnvironment: The current runtime environment.
        """
        env_value = EnvManager._get(EnvManager.EnvVariables.ENVIRONMENT)
        if env_value:
            env_lower = env_value.lower()
            if env_lower == EnvManager.RuntimeEnvironment.DEVELOPMENT.value:
                return EnvManager.RuntimeEnvironment.DEVELOPMENT
            if env_lower == EnvManager.RuntimeEnvironment.TESTING.value:
                return EnvManager.RuntimeEnvironment.TESTING
        return EnvManager.RuntimeEnvironment.PRODUCTION

    @staticmethod
    def get_database_url() -> str:
        """Retrieves the database URL from environment variables.

        Returns:
            str: The database URL.

        Raises:
            EnvironmentError: If the DATABASE_URL environment variable is not set.
        """
        from svs_core.shared.logger import get_logger

        db_url = EnvManager._get(EnvManager.EnvVariables.DATABASE_URL)
        if not db_url:
            logger = get_logger(__name__)
            logger.error("DATABASE_URL environment variable not set.")
            raise EnvironmentError("DATABASE_URL environment variable not set.")
        return db_url
