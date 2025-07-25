import logging
import shlex
import subprocess
from typing import Mapping, Optional

from svs_core.shared.logger import get_logger


def run_command(
    command: str, env: Optional[Mapping[str, str]] = None, check: bool = True
) -> subprocess.CompletedProcess[str]:
    """
    Executes a shell command with optional environment variables.

    Args:
        command (str): The shell command to execute.
        env (Optional[Mapping[str, str]]): Environment variables to use.
        check (bool): If True, raises CalledProcessError on non-zero exit.

    Returns:
        subprocess.CompletedProcess: The result of the executed command.
    """
    get_logger(__name__).log(
        logging.DEBUG, f"Executing {command} ENV: {env}, check = {check}"
    )

    exec_env = dict(env) if env else {}  # TODO: maybe inject system env?

    cmd_list = shlex.split(command)

    result = subprocess.run(
        cmd_list, env=exec_env, check=check, capture_output=True, text=True
    )

    get_logger(__name__).log(logging.DEBUG, result)

    return result
