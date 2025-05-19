import logging
import os
import time

_logger_instances = {}


def get_logger(name=None) -> logging.Logger:
    if name is None:
        name = "unknown"

    if name in _logger_instances:
        return _logger_instances[name]

    env = os.getenv("ENV", "development")
    logger = logging.getLogger(name)
    logger.handlers.clear()

    class UTCFormatter(logging.Formatter):
        converter = time.gmtime

    formatter = UTCFormatter("%(asctime)s: %(name)s[%(levelname)s] - %(message)s")
    handler: logging.Handler

    if env == "production":
        handler = logging.FileHandler("svs-core.log")
        handler.setLevel(logging.INFO)
    else:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    _logger_instances[name] = logger

    return logger
