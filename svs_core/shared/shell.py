import grp
import logging
import os
import pwd
import shlex
import shutil
import stat
import subprocess

from pathlib import Path
from typing import Mapping


def create_directory(
    path: str, logger: logging.Logger | None = None, user: str = "svs"
) -> None:
    """Creates a directory at the specified path if it does not exist.

    Sets ownership to user:svs-admins and permissions to 770 (rwxrwx---) for the
    final directory in the path. Parent directories are created with default
    permissions, and only the final directory gets the specified permissions.

    Args:
        path (str): The directory path to create.
        logger (logging.Logger | None): custom log handler.
        user (str): The user to create the directory as.
    """
    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    os.makedirs(path, exist_ok=True)

    try:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG)
    except OSError:
        logger.warning("Could not set permissions for %s", path)

    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = grp.getgrnam("svs-admins").gr_gid
        os.chown(path, uid, gid)
    except (KeyError, OSError):
        logger.warning("Could not set ownership for %s", path)


def remove_directory(
    path: str, logger: logging.Logger | None = None, user: str = "svs"
) -> None:
    """Removes a directory at the specified path if it exists.

    Args:
        path (str): The directory path to remove.
        logger (logging.Logger | None): custom log handler.
        user (str): Unused, retained for backward compatibility.
    """
    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    shutil.rmtree(path, ignore_errors=True)


def read_file(path: Path, logger: logging.Logger | None = None) -> str:
    """Reads the content of a file at the specified path.

    Args:
        path (Path): The file path to read.
        logger (logging.Logger | None): custom log handler.

    Returns:
        str: The content of the file.
    """

    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    logger.log(logging.DEBUG, "Reading file at path: %s", path.as_posix())

    return path.read_text()


def run_command(
    command: str,
    env: Mapping[str, str] | None = None,
    check: bool = True,
    user: str = "svs",
    logger: logging.Logger | None = None,
) -> subprocess.CompletedProcess[str]:
    """Executes a shell command with optional environment variables.

    Always runs in shell mode to support shell operators (||, &&, etc.).

    Args:
        command (str): The shell command to execute.
        env (Mapping[str, str] | None): Environment variables to use.
        check (bool): If True, raises CalledProcessError on non-zero exit.
        user (str): The user to run the command as.
        logger (logging.Logger | None): custom log handler.

    Returns:
        subprocess.CompletedProcess: The result of the executed command.
    """

    exec_env = dict(env) if env else {}
    exec_env.update({"DJANGO_SETTINGS_MODULE": "svs_core.db.settings"})

    base = (
        f"sudo -u {shlex.quote(user)} "
        if not command.strip().startswith("sudo")
        else ""
    )

    command = f"{base}{command}"

    if not logger:
        from svs_core.shared.logger import get_logger

        logger = get_logger(__name__)

    logger.log(
        logging.DEBUG,
        "Executing shell command (details redacted): user=%s, check=%s, has_env=%s, command_length=%s",
        user,
        check,
        bool(exec_env),
        len(command),
    )

    result = subprocess.run(
        command, env=exec_env, check=check, capture_output=True, text=True, shell=True
    )

    logger.log(logging.DEBUG, result)

    return result
