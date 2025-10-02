import logging
import os
import time

from pathlib import Path

import pytest

from svs_core.shared.logger import clear_loggers, get_logger


class TestLogger:
    @pytest.fixture(autouse=True)
    def reset_logger(self):
        clear_loggers()

        if "ENV" in os.environ:
            del os.environ["ENV"]

    @pytest.mark.unit
    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger("test")
        logger2 = get_logger("test")

        assert logger1 is logger2

    @pytest.mark.unit
    def test_get_logger_default_name(self):
        """Test that get_logger returns a logger with the default name if none
        is provided."""
        default_logger = get_logger()

        assert isinstance(default_logger, logging.Logger)
        assert default_logger.name == "unknown"

    @pytest.mark.unit
    def test_stream_handler_in_development(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Test that the logger outputs to stdout in development mode."""
        os.environ.pop("ENV", None)

        logger = get_logger("dev_test")
        logger.debug("hello dev")

        captured = capsys.readouterr()

        assert "[DEBUG] dev_test" in captured.out
        assert "hello dev" in captured.out

    @pytest.mark.unit
    def test_file_handler_in_production(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that the logger outputs to a file in production mode."""
        monkeypatch.setenv("ENV", "production")

        log_file = tmp_path / "svs-core.log"
        monkeypatch.chdir(tmp_path)

        logger = get_logger("prod_test")
        logger.info("hello prod")
        time.sleep(0.1)

        content = log_file.read_text()

        assert "[INFO] prod_test" in content
        assert "hello prod" in content
