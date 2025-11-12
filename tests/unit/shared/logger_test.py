import logging
import os
import time

from pathlib import Path

import pytest

from pytest_mock import MockerFixture

from svs_core.shared.env_manager import EnvManager
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
        self,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test that the logger outputs to stdout in development mode."""
        mocker.patch(
            "svs_core.shared.env_manager.EnvManager.get_runtime_environment",
            return_value=EnvManager.RuntimeEnvironment.DEVELOPMENT,
        )
        print("Current ENV:", EnvManager.get_runtime_environment())
        logger = get_logger("dev_test")
        logger.debug("hello dev")

        captured = capsys.readouterr()

        assert "[DEBUG] dev_test" in captured.out
        assert "hello dev" in captured.out

    @pytest.mark.unit
    def test_file_handler_in_production(
        self, tmp_path: Path, mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that the logger outputs to a file in production mode."""
        # Create a temporary log file
        log_file = tmp_path / "svs-core.log"
        log_file.write_text("")  # Create the actual file

        mocker.patch(
            "svs_core.shared.env_manager.EnvManager.get_runtime_environment",
            return_value=EnvManager.RuntimeEnvironment.PRODUCTION,
        )

        # Mock the Path constructor to return our temp log file
        def mock_path(path_str):
            if "svs.log" in path_str:
                # Return the actual Path object pointing to our temp file
                return log_file
            return Path(path_str)

        mocker.patch(
            "svs_core.shared.logger.Path",
            side_effect=mock_path,
        )

        logger = get_logger("prod_test")
        logger.info("hello prod")
        time.sleep(0.1)

        # Verify file handler was created
        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert (
            len(file_handlers) > 0
        ), "FileHandler should be created in production mode"

        # Flush the handler to ensure data is written
        for handler in file_handlers:
            handler.flush()

        # Read and verify the log file content
        content = log_file.read_text()
        assert "[INFO] prod_test" in content
        assert "hello prod" in content
