import subprocess

from pathlib import Path
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
    def test_create_directory_basic(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chmod = mocker.patch("os.chmod")
        mock_chown = mocker.patch("os.chown")
        mock_getpwnam = mocker.patch("pwd.getpwnam")
        mock_getgrnam = mocker.patch("grp.getgrnam")
        mock_getpwnam.return_value.pw_uid = 1000
        mock_getgrnam.return_value.gr_gid = 2000

        test_dir = tmp_path / "test_dir"
        create_directory(str(test_dir))

        mock_makedirs.assert_called_once_with(str(test_dir), exist_ok=True)
        mock_chmod.assert_called_once()
        mock_getpwnam.assert_called_once_with("svs")
        mock_getgrnam.assert_called_once_with("svs-admins")
        mock_chown.assert_called_once_with(str(test_dir), 1000, 2000)

    @pytest.mark.unit
    def test_create_directory_with_logger(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chmod = mocker.patch("os.chmod")
        mock_chown = mocker.patch("os.chown")
        mock_getpwnam = mocker.patch("pwd.getpwnam")
        mock_getgrnam = mocker.patch("grp.getgrnam")
        mock_getpwnam.return_value.pw_uid = 1000
        mock_getgrnam.return_value.gr_gid = 2000
        mock_logger = mocker.MagicMock()

        test_dir = tmp_path / "test_dir"
        create_directory(str(test_dir), logger=mock_logger)

        mock_makedirs.assert_called_once_with(str(test_dir), exist_ok=True)
        mock_chmod.assert_called_once()
        mock_getpwnam.assert_called_once_with("svs")
        mock_getgrnam.assert_called_once_with("svs-admins")
        mock_chown.assert_called_once_with(str(test_dir), 1000, 2000)

    @pytest.mark.unit
    def test_create_directory_multiple_paths(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_makedirs = mocker.patch("os.makedirs")
        mock_chmod = mocker.patch("os.chmod")
        mock_chown = mocker.patch("os.chown")
        mock_getpwnam = mocker.patch("pwd.getpwnam")
        mock_getgrnam = mocker.patch("grp.getgrnam")
        mock_getpwnam.return_value.pw_uid = 1000
        mock_getgrnam.return_value.gr_gid = 2000

        test_dir = tmp_path / "my test directory"
        create_directory(str(test_dir))

        mock_makedirs.assert_called_once_with(str(test_dir), exist_ok=True)
        mock_chmod.assert_called_once()
        mock_chown.assert_called_once()

    @pytest.mark.unit
    def test_remove_directory_basic(self, mocker: MockerFixture) -> None:
        mock_rmtree = mocker.patch("shutil.rmtree")

        remove_directory("/tmp/test_dir")

        mock_rmtree.assert_called_once_with("/tmp/test_dir", ignore_errors=True)

    @pytest.mark.unit
    def test_remove_directory_with_logger(self, mocker: MockerFixture) -> None:
        mock_rmtree = mocker.patch("shutil.rmtree")
        mock_logger = mocker.MagicMock()

        remove_directory("/tmp/test_dir", logger=mock_logger)

        mock_rmtree.assert_called_once_with("/tmp/test_dir", ignore_errors=True)

    @pytest.mark.unit
    def test_remove_directory_with_spaces(self, mocker: MockerFixture) -> None:
        mock_rmtree = mocker.patch("shutil.rmtree")

        remove_directory("/tmp/my test directory")

        mock_rmtree.assert_called_once_with(
            "/tmp/my test directory", ignore_errors=True
        )


class TestFileReading:
    @pytest.mark.unit
    def test_read_file_success(self, mocker: MockerFixture, tmp_path: Path) -> None:
        test_file = tmp_path / "test.txt"
        test_file.write_text("file content here\n")

        result = read_file(test_file)

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
