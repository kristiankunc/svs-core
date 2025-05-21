import os
import logging
import time
import pytest
from typing import Any
from svs_core.shared.logger import get_logger, clear_loggers


@pytest.fixture(autouse=True)  # type: ignore
def reset_logger() -> None:
    clear_loggers()

    if "ENV" in os.environ:
        del os.environ["ENV"]


def test_get_logger_returns_same_instance() -> None:
    """Test that get_logger returns the same instance for the same name."""

    logger1 = get_logger("test")
    logger2 = get_logger("test")

    assert logger1 is logger2


def test_get_logger_default_name() -> None:
    """Test that get_logger returns a logger with the default name if none is provided."""

    default_logger = get_logger()

    assert isinstance(default_logger, logging.Logger)
    assert default_logger.name == "unknown"


def test_stream_handler_in_development(capsys: Any) -> None:
    """Test that the logger outputs to stdout in development mode."""

    os.environ.pop("ENV", None)

    logger = get_logger("dev_test")
    logger.debug("hello dev")

    captured = capsys.readouterr()

    assert "dev_test[DEBUG]" in captured.out
    assert "hello dev" in captured.out


def test_file_handler_in_production(tmp_path: Any, monkeypatch: Any) -> None:
    """Test that the logger outputs to a file in production mode."""

    monkeypatch.setenv("ENV", "production")

    log_file = tmp_path / "svs-core.log"
    monkeypatch.chdir(tmp_path)

    logger = get_logger("prod_test")
    logger.info("hello prod")
    time.sleep(0.1)

    content = log_file.read_text()

    assert "prod_test[INFO]" in content
    assert "hello prod" in content
