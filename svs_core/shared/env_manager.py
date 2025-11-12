from __future__ import annotations

import logging
import os
import subprocess

from enum import Enum
from pathlib import Path
from types import MappingProxyType

from svs_core.shared.logger import get_logger
from svs_core.shared.shell import read_file, run_command


class EnvManager:
    """Manages reading and caching environment variables from a .env file."""

    ENV_FILE_PATH = Path("/etc/svs/.env")

    class RuntimeEnvironment(Enum):
        """Enumeration of runtime environments."""

        DEVELOPMENT = "development"
        PRODUCTION = "production"

    class EnvVariables(Enum):
        """Enumeration of environment variable keys."""

        ENVIRONMENT = "ENVIRONMENT"
        DATABASE_URL = "DATABASE_URL"

    @staticmethod
    def load_env_file() -> None:
        """Loads environment variables from the .env file.

        Raises:
            FileNotFoundError: If the .env file does not exist.
        """

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
                os.environ[key.strip()] = value.strip().replace('"', "")

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
        if env_value and env_value.lower() == "development":
            return EnvManager.RuntimeEnvironment.DEVELOPMENT
        return EnvManager.RuntimeEnvironment.PRODUCTION

    @staticmethod
    def get_database_url() -> str:
        """Retrieves the database URL from environment variables.

        Returns:
            str: The database URL.

        Raises:
            EnvironmentError: If the DATABASE_URL environment variable is not set.
        """
        db_url = EnvManager._get(EnvManager.EnvVariables.DATABASE_URL)
        if not db_url:
            logger = get_logger(__name__)
            logger.error("DATABASE_URL environment variable not set.")
            raise EnvironmentError("DATABASE_URL environment variable not set.")
        return db_url
