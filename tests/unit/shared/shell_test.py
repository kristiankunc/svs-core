import subprocess
from typing import Dict

import pytest
from pytest_mock import MockerFixture

from svs_core.shared.shell import run_command


class TestCommandExecution:
    @pytest.mark.unit
    def test_basic_command_execution(self, mocker: MockerFixture) -> None:
        """Test that a basic command is executed correctly."""

        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "mocked output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = run_command("echo hello")

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert ["echo", "hello"] == args[0]
        assert {} == kwargs.get("env", {})
        assert True == kwargs.get("check", False)

        assert "mocked output" == result.stdout

    @pytest.mark.unit
    def test_command_with_environment(self, mocker: MockerFixture) -> None:
        """Test that environment variables are correctly passed."""

        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        test_env: Dict[str, str] = {"TEST_VAR": "test_value"}

        run_command("echo $TEST_VAR", env=test_env)

        _, kwargs = mock_run.call_args
        assert test_env == kwargs.get("env", {})

    @pytest.mark.unit
    def test_command_with_check_false(self, mocker: MockerFixture) -> None:
        """Test that check=False is correctly passed."""

        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        run_command("ls non_existent_dir", check=False)

        _, kwargs = mock_run.call_args
        assert False == kwargs.get("check", True)

    @pytest.mark.unit
    def test_output_capturing(self, mocker: MockerFixture) -> None:
        """Test that command output is correctly captured."""

        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "expected stdout"
        mock_process.stderr = "expected stderr"
        mock_run.return_value = mock_process

        result = run_command("echo test")

        assert "expected stdout" == result.stdout
        assert "expected stderr" == result.stderr

    @pytest.mark.unit
    def test_error_handling(self, mocker: MockerFixture) -> None:
        """Test that errors are properly propagated when check=True."""

        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["failing", "command"], output="", stderr="command failed"
        )

        with pytest.raises(subprocess.CalledProcessError):
            run_command("failing command")

        _, kwargs = mock_run.call_args
        assert True == kwargs.get("check", False)
