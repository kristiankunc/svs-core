import logging
import sys
import time

from pathlib import Path
from typing import Optional

from svs_core.shared.env_manager import EnvManager

_logger_instances: dict[str, logging.Logger] = {}


def _is_verbose_mode() -> bool:
    """Check if verbose mode is enabled using CLI state."""
    # Import here to avoid circular imports
    from svs_core.cli.state import is_verbose

    return is_verbose()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Returns a logger instance with the specified name.

    If a logger with the same name already exists, it returns the existing instance.
    The logger is configured to log messages in UTC format.

    Args:
        name (Optional[str]): The name of the logger. If None, defaults to "unknown".

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

    # Try to use file handler if log file exists, otherwise use stream handler
    LOG_FILE = Path("/etc/svs/svs.log")
    handler: logging.Handler = (
        logging.FileHandler(LOG_FILE.as_posix())
        if LOG_FILE.exists()
        else logging.StreamHandler(sys.stdout)
    )

    if EnvManager.get_runtime_environment() == EnvManager.RuntimeEnvironment.PRODUCTION:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # If verbose mode is enabled, add the verbose handler to this new logger
    if _is_verbose_mode():
        verbose_formatter = logging.Formatter("%(levelname)s: %(name)s %(message)s")
        verbose_handler = logging.StreamHandler(sys.stdout)
        verbose_handler.setLevel(logging.DEBUG)
        verbose_handler.setFormatter(verbose_formatter)
        logger.addHandler(verbose_handler)

    _logger_instances[name] = logger

    return logger


def add_verbose_handler() -> None:
    """Add a stdout handler to all existing loggers for verbose output.

    This function is safe to call multiple times - it will only add a verbose
    handler to loggers that don't already have one.
    """
    for logger in _logger_instances.values():
        # Check if this logger already has a verbose handler
        has_verbose_handler = any(
            isinstance(h, logging.StreamHandler)
            and h.stream == sys.stdout
            and h.level == logging.DEBUG
            and "%(levelname)s: %(name)s"
            in (h.formatter._fmt or "" if h.formatter else "")
            for h in logger.handlers
        )
        if has_verbose_handler:
            continue

        # Create a new handler for each logger
        formatter = logging.Formatter("%(levelname)s: %(name)s %(message)s")
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def clear_loggers() -> None:
    """Clears all stored logger instances."""
    _logger_instances.clear()
