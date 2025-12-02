import logging
import os
import time

from pathlib import Path

import pytest

from pytest_mock import MockerFixture

from svs_core.shared.logger import add_verbose_handler, clear_loggers, get_logger


class TestLogger:
    @pytest.fixture(autouse=True)
    def reset_logger(self):
        clear_loggers()

        if "ENV" in os.environ:
            del os.environ["ENV"]

    @pytest.mark.unit
    def test_get_logger_returns_same_instance(self) -> None:
        logger1 = get_logger("test")
        logger2 = get_logger("test")

        assert logger1 is logger2

    @pytest.mark.unit
    def test_get_logger_default_name(self) -> None:
        default_logger = get_logger()

        assert isinstance(default_logger, logging.Logger)
        assert default_logger.name == "unknown"

    @pytest.mark.unit
    def test_stream_handler_when_log_file_not_exists(
        self,
        capsys: pytest.CaptureFixture[str],
        mocker: MockerFixture,
    ) -> None:
        # Mock Path to return False for exists() - simulating no log file
        mock_path_instance = mocker.MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.as_posix.return_value = "/etc/svs/svs.log"

        mock_path = mocker.patch("svs_core.shared.logger.Path")
        mock_path.return_value = mock_path_instance

        logger = get_logger("dev_test")
        logger.debug("hello dev")

        # When log file doesn't exist, NullHandler is used, so no output
        null_handlers = [
            h for h in logger.handlers if isinstance(h, logging.NullHandler)
        ]
        assert (
            len(null_handlers) > 0
        ), "NullHandler should be created when log file doesn't exist"

    @pytest.mark.unit
    def test_file_handler_when_log_file_exists(
        self, tmp_path: Path, mocker: MockerFixture
    ) -> None:
        log_file = tmp_path / "svs.log"
        log_file.write_text("")

        # Mock Path to return True for exists() and the temp log file path
        mock_path_class = mocker.patch("svs_core.shared.logger.Path")

        def path_side_effect(path_str):
            if isinstance(path_str, str) and "svs.log" in path_str:
                return log_file
            return Path(path_str)

        mock_path_class.side_effect = path_side_effect
        # Make exists() return True for the log file
        log_file_mock = mocker.MagicMock()
        log_file_mock.exists.return_value = True
        log_file_mock.as_posix.return_value = str(log_file)
        mock_path_class.return_value = log_file_mock

        logger = get_logger("prod_test")
        logger.info("hello prod")
        time.sleep(0.1)

        file_handlers = [
            h for h in logger.handlers if isinstance(h, logging.FileHandler)
        ]
        assert (
            len(file_handlers) > 0
        ), "FileHandler should be created when log file exists"

        for handler in file_handlers:
            handler.flush()

        content = log_file.read_text()
        assert "[INFO] prod_test" in content
        assert "hello prod" in content

    @pytest.mark.unit
    def test_add_verbose_handler(
        self, capsys: pytest.CaptureFixture[str], mocker: MockerFixture
    ) -> None:
        # Mock Path to use stdout handler
        mock_path = mocker.patch("svs_core.shared.logger.Path")
        mock_path.return_value.exists.return_value = False

        logger = get_logger("verbose_test")
        add_verbose_handler()

        logger.debug("verbose message")

        captured = capsys.readouterr()

        assert "DEBUG: verbose_test verbose message" in captured.out
