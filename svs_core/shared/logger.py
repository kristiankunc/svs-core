import logging
import os
import sys
import time
from typing import Optional

_logger_instances: dict[str, logging.Logger] = {}


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger instance with the specified name. If no name is provided, it uses the module's name.
    If a logger with the same name already exists, it returns the existing instance.
    The logger is configured to log messages in UTC format.

    Args:
        name (Optional[str]): The name of the logger. If None, uses the module's name.
    Returns:
        logging.Logger: The logger instance.
    """

    if name is None:
        name = "unknown"

    if name in _logger_instances:
        return _logger_instances[name]

    env = os.getenv("ENV", "development")
    logger = logging.getLogger(name)
    logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    class UTCFormatter(logging.Formatter):
        converter = time.gmtime

    formatter = UTCFormatter("%(asctime)s: [%(levelname)s] %(name)s %(message)s")
    handler: logging.Handler

    if env == "production":
        handler = logging.FileHandler("svs-core.log")
        handler.setLevel(logging.INFO)
    else:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _logger_instances[name] = logger

    return logger


def clear_loggers() -> None:
    """
    Clears all stored logger instances.
    """
    _logger_instances.clear()
