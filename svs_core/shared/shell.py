import logging
import subprocess

from pathlib import Path
from typing import Mapping, Optional


def create_directory(
    path: str, logger: Optional[logging.Logger] = None, user: str = "svs"
) -> None:
    """Creates a directory at the specified path if it does not exist.

    Sets ownership to user:svs-admins and permissions to 770 (rwxrwx---) for the
    final directory in the path. When using mkdir -p, parent directories are created
    with default permissions, and only the final directory gets the specified permissions.

    Args:
        path (str): The directory path to create.
        logger (Optional[logging.Logger]): custom log handler.
        user (str): The user to create the directory as.
    """
    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    command = f"mkdir -p {path}"

    run_command(command, user=user, logger=logger)

    # Set ownership to user:svs-admins and permissions to 770
    # This applies to the final directory and all parent directories created by mkdir -p
    run_command(f"sudo chown {user}:svs-admins {path}", check=True, logger=logger)
    run_command(f"sudo chmod 770 {path}", check=True, logger=logger)


def remove_directory(
    path: str, logger: Optional[logging.Logger] = None, user: str = "svs"
) -> None:
    """Removes a directory at the specified path if it exists.

    Args:
        path (str): The directory path to remove.
        logger (Optional[logging.Logger]): custom log handler.
        user (str): The user to remove the directory as.
    """
    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    command = f"rm -rf {path}"
    run_command(command, logger=logger, user=user)


def read_file(path: Path, logger: Optional[logging.Logger] = None) -> str:
    """Reads the content of a file at the specified path.

    Args:
        path (Path): The file path to read.
        logger (Optional[logging.Logger]): custom log handler.

    Returns:
        str: The content of the file.
    """

    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    command = f"cat {path.as_posix()}"
    logger.log(logging.DEBUG, f"Reading file at path: {path.as_posix()}")

    result = subprocess.run(
        command, shell=True, check=True, capture_output=True, text=True
    )

    return result.stdout


def run_command(
    command: str,
    env: Optional[Mapping[str, str]] = None,
    check: bool = True,
    user: str = "svs",
    logger: Optional[logging.Logger] = None,
) -> subprocess.CompletedProcess[str]:
    """Executes a shell command with optional environment variables.

    Always runs in shell mode to support shell operators (||, &&, etc.).

    Args:
        command (str): The shell command to execute.
        env (Optional[Mapping[str, str]]): Environment variables to use.
        check (bool): If True, raises CalledProcessError on non-zero exit.
        user (str): The user to run the command as.
        logger (Optional[logging.Logger]): custom log handler.

    Returns:
        subprocess.CompletedProcess: The result of the executed command.
    """

    exec_env = dict(env) if env else {}
    exec_env.update({"DJANGO_SETTINGS_MODULE": "svs_core.db.settings"})

    base = f"sudo -u {user} " if not command.strip().startswith("sudo") else ""

    command = f"{base}{command}"

    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    logger.log(logging.DEBUG, f"Executing command: {command} with env: {exec_env}")

    result = subprocess.run(
        command, env=exec_env, check=check, capture_output=True, text=True, shell=True
    )

    logger.log(logging.DEBUG, result)

    return result
