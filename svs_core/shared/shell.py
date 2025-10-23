import logging
import subprocess

from typing import Mapping, Optional


def run_command(
    command: str,
    env: Optional[Mapping[str, str]] = None,
    check: bool = True,
    use_svs_user: bool = True,
    logger: Optional[logging.Logger] = None,
) -> subprocess.CompletedProcess[str]:
    """Executes a shell command with optional environment variables.

    Always runs in shell mode to support shell operators (||, &&, etc.).

    Args:
        command (str): The shell command to execute.
        env (Optional[Mapping[str, str]]): Environment variables to use.
        check (bool): If True, raises CalledProcessError on non-zero exit.
        use_svs_user (bool): If True, runs the command as the 'svs' system user.
        logger (Optional[logging.Logger]): custom log handler.

    Returns:
        subprocess.CompletedProcess: The result of the executed command.
    """

    exec_env = dict(env) if env else {}  # TODO: maybe inject system env?
    exec_env.update({"DJANGO_SETTINGS_MODULE": "svs_core.db.settings"})

    base = ""
    if use_svs_user:
        base = "sudo -u svs " if not command.strip().startswith("sudo") else ""

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
