import os
import logging
import subprocess
import pytest
import pathlib
from svs_core.shared.base import BaseClass, Executable


def test_get_logger_console(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "development")
    logger = BaseClass.get_logger("test_logger")

    assert isinstance(logger, logging.Logger)
    assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    assert logger.level == logging.DEBUG


def test_get_logger_file(
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: pathlib.Path) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.chdir(tmp_path)
    logger = BaseClass.get_logger("file_logger")

    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)

    logger.info("test message")
    logger.handlers[0].flush()

    assert os.path.exists("svs-core.log")

    with open("svs-core.log", "r") as f:
        content = f.read()
    assert "test message" in content


def test_executable_execute_success() -> None:
    exe = Executable()
    result = exe.execute("echo hello")

    assert result.returncode == 0
    assert "hello" in result.stdout


def test_executable_execute_failure() -> None:
    exe = Executable()

    with pytest.raises(subprocess.CalledProcessError):
        exe.execute("exit 1")


def test_executable_execute_failure_no_check() -> None:
    exe = Executable()

    result = exe.execute("exit 1", check=False)
    assert result.returncode == 1
