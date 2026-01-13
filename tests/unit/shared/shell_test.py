import subprocess

from typing import Dict

import pytest

from pytest_mock import MockerFixture

from svs_core.shared.shell import (
    create_directory,
    read_file,
    remove_directory,
    run_command,
)


class TestDirectoryManagement:
    @pytest.mark.unit
    def test_create_directory_basic(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_run.return_value = mock_process

        create_directory("/tmp/test_dir")

        # create_directory now makes 3 calls: mkdir, chown, chmod
        assert mock_run.call_count == 3

        # First call should be mkdir
        args, kwargs = mock_run.call_args_list[0]
        assert "sudo -u svs mkdir -p /tmp/test_dir" == args[0]
        assert kwargs.get("shell", False)
        assert kwargs.get("check", False)

        # Second call should be chown
        args, kwargs = mock_run.call_args_list[1]
        assert "sudo chown svs:svs-admins /tmp/test_dir" == args[0]

        # Third call should be chmod
        args, kwargs = mock_run.call_args_list[2]
        assert "sudo chmod 770 /tmp/test_dir" == args[0]

    @pytest.mark.unit
    def test_create_directory_with_logger(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_logger = mocker.MagicMock()
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_run.return_value = mock_process

        create_directory("/tmp/test_dir", logger=mock_logger)

        mock_logger.log.assert_called()
        # create_directory now makes 3 calls: mkdir, chown, chmod
        assert mock_run.call_count == 3

    @pytest.mark.unit
    def test_create_directory_multiple_paths(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="sudo -u svs mkdir -p /tmp/my test directory",
            output="",
            stderr="error",
        )

        with pytest.raises(subprocess.CalledProcessError):
            create_directory("/tmp/my test directory")

        # Should fail on the first call (mkdir)
        mock_run.assert_called_once()

    @pytest.mark.unit
    def test_remove_directory_basic(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_run.return_value = mock_process

        remove_directory("/tmp/test_dir")

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "sudo -u svs rm -rf /tmp/test_dir" == args[0]
        assert kwargs.get("shell", False)
        assert kwargs.get("check", False)

    @pytest.mark.unit
    def test_remove_directory_with_logger(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_logger = mocker.MagicMock()
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_run.return_value = mock_process

        remove_directory("/tmp/test_dir", logger=mock_logger)

        mock_logger.log.assert_called()
        mock_run.assert_called_once()

    @pytest.mark.unit
    def test_remove_directory_with_spaces(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1,
            cmd="sudo -u svs rm -rf /tmp/my test directory",
            output="",
            stderr="error",
        )

        with pytest.raises(subprocess.CalledProcessError):
            remove_directory("/tmp/my test directory")

        mock_run.assert_called_once()


class TestFileReading:
    @pytest.mark.unit
    def test_read_file_success(self, mocker: MockerFixture) -> None:
        from pathlib import Path

        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "file content here\n"
        mock_run.return_value = mock_process

        result = read_file(Path("/tmp/test.txt"))

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "cat /tmp/test.txt" == args[0]
        assert kwargs.get("shell", False)
        assert kwargs.get("check", False)
        assert "file content here\n" == result


class TestCommandExecution:
    @pytest.mark.unit
    def test_basic_command_execution(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "mocked output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        result = run_command("echo hello")

        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        assert "sudo -u svs echo hello" == args[0]
        assert {"DJANGO_SETTINGS_MODULE": "svs_core.db.settings"} == kwargs.get(
            "env", {}
        )
        assert kwargs.get("check", False)
        assert kwargs.get("shell", False)

        assert "mocked output" == result.stdout

    @pytest.mark.unit
    def test_command_with_environment(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        test_env: Dict[str, str] = {"TEST_VAR": "test_value"}

        run_command("echo $TEST_VAR", env=test_env)

        args, kwargs = mock_run.call_args
        expected_env = {
            "TEST_VAR": "test_value",
            "DJANGO_SETTINGS_MODULE": "svs_core.db.settings",
        }
        assert "sudo -u svs echo $TEST_VAR" == args[0]
        assert expected_env == kwargs.get("env", {})
        assert kwargs.get("shell", False)

    @pytest.mark.unit
    def test_command_with_check_false(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "test output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        run_command("ls non_existent_dir", check=False)

        args, kwargs = mock_run.call_args
        assert "sudo -u svs ls non_existent_dir" == args[0]
        assert not kwargs.get("check", True)
        assert kwargs.get("shell", False)

    @pytest.mark.unit
    def test_output_capturing(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "expected stdout"
        mock_process.stderr = "expected stderr"
        mock_run.return_value = mock_process

        result = run_command("echo test")

        args, kwargs = mock_run.call_args
        assert "sudo -u svs echo test" == args[0]
        assert kwargs.get("shell", False)
        assert "expected stdout" == result.stdout
        assert "expected stderr" == result.stderr

    @pytest.mark.unit
    def test_error_handling(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd="failing command", output="", stderr="command failed"
        )

        with pytest.raises(subprocess.CalledProcessError):
            run_command("failing command")

        args, kwargs = mock_run.call_args
        assert "sudo -u svs failing command" == args[0]
        assert kwargs.get("check", False)
        assert kwargs.get("shell", False)

    @pytest.mark.unit
    def test_shell_operators(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_process = mocker.MagicMock(spec=subprocess.CompletedProcess)
        mock_process.stdout = "command output"
        mock_process.stderr = ""
        mock_run.return_value = mock_process

        run_command("test -f /non_existent_file || echo 'file not found'")

        args, kwargs = mock_run.call_args
        assert (
            "sudo -u svs test -f /non_existent_file || echo 'file not found'" == args[0]
        )
        assert kwargs.get("shell", False)

        run_command("mkdir -p test_dir && echo 'dir created'")

        args, kwargs = mock_run.call_args
        assert "sudo -u svs mkdir -p test_dir && echo 'dir created'" == args[0]
        assert kwargs.get("shell", False)
