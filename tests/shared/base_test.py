import subprocess
import os
import pytest
from unittest.mock import patch, MagicMock
from svs_core.shared.base import BaseClass, Executable

@pytest.fixture
def mock_logger():
    with patch("svs_core.shared.base.logging.getLogger") as mock_get_logger:
        mock_logger_instance = MagicMock()
        mock_get_logger.return_value = mock_logger_instance
        yield mock_logger_instance

@patch("svs_core.shared.base.logging.getLogger")
def test_logger_initialization(mock_get_logger, mock_logger):
    base = BaseClass(is_loggable=True)
    assert base.logger is not None
    mock_get_logger.assert_called_once()

@patch.dict(os.environ, {"ENV": "production"})
@patch("svs_core.shared.base.logging.getLogger")
@patch("svs_core.shared.base.logging.FileHandler")
def test_logger_in_production(mock_file_handler, mock_get_logger):
    mock_logger_instance = MagicMock()
    mock_logger_instance.handlers = []
    mock_get_logger.return_value = mock_logger_instance
    BaseClass.get_logger("TestLogger")
    mock_file_handler.assert_called_once_with("svs-core.log")

@patch.dict(os.environ, {"ENV": "development"})
@patch("svs_core.shared.base.logging.getLogger")
@patch("svs_core.shared.base.logging.StreamHandler")
def test_logger_in_development(mock_stream_handler, mock_get_logger):
    mock_logger_instance = MagicMock()
    mock_logger_instance.handlers = []
    mock_get_logger.return_value = mock_logger_instance
    BaseClass.get_logger("TestLogger")
    mock_stream_handler.assert_called_once()

@patch("subprocess.run")
def test_execute_success(mock_run):
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Success"
    mock_run.return_value = mock_result

    executable = Executable()
    result = executable.execute("echo 'Hello'")
    assert result.stdout == "Success"
    mock_run.assert_called_once_with("echo 'Hello'", shell=True, check=True, capture_output=True, text=True)

@patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd", stderr="Error"))
def test_execute_failure(mock_run):
    executable = Executable()
    result = executable.execute("invalid_command", check=False)
    assert result.stderr == "Error"
    mock_run.assert_called_once()

@patch("subprocess.run", side_effect=Exception("Unexpected error"))
def test_execute_unexpected_error(mock_run):
    executable = Executable()
    with pytest.raises(Exception, match="Unexpected error"):
        executable.execute("invalid_command")
    mock_run.assert_called_once()