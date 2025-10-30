import logging
import sys
import time

from pathlib import Path
from typing import Optional

_logger_instances: dict[str, logging.Logger] = {}


def get_logger(name: Optional[str] = None, independent: bool = False) -> logging.Logger:
    """Returns a logger instance with the specified name.

    If no name is provided, it uses the module's name. If a logger with the same name already
    exists, it returns the existing instance. The logger is configured to log
    messages in UTC format.

    Args:
        name (Optional[str]): The name of the logger. If None, uses the module's name.
        independent (bool): Whether the logger should configure based on EnvManager. Should be used only in EnvManager to avoid circular dependency

    Returns:
        logging.Logger: The logger instance.
    """

    if name is None:
        name = "unknown"

    if name in _logger_instances:
        return _logger_instances[name]

    logger = logging.getLogger(name)
    logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    class UTCFormatter(logging.Formatter):
        @staticmethod
        def converter(timestamp: float | None) -> time.struct_time:
            return time.gmtime(timestamp)

    formatter = UTCFormatter("%(asctime)s: [%(levelname)s] %(name)s %(message)s")
    handler: logging.Handler = logging.NullHandler()

    LOG_FILE = Path("/etc/svs/svs.log")

    if not independent:
        from svs_core.shared.env_manager import EnvManager

        match EnvManager.get_runtime_environment():
            case EnvManager.RuntimeEnvironment.DEVELOPMENT:
                handler = logging.StreamHandler(sys.stdout)
                handler.setLevel(logging.DEBUG)
            case EnvManager.RuntimeEnvironment.PRODUCTION:
                handler = logging.FileHandler(LOG_FILE.as_posix())
                handler.setLevel(logging.DEBUG)

    else:
        handler = logging.FileHandler(LOG_FILE.as_posix())
        handler.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _logger_instances[name] = logger

    return logger


def clear_loggers() -> None:
    """Clears all stored logger instances."""
    _logger_instances.clear()
