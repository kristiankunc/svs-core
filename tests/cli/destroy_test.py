"""Unit tests for svs_core.cli.destroy module."""

from __future__ import annotations

import os

from pathlib import Path

import pytest
import typer

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app
from svs_core.cli import destroy as destroy_module


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


class TestStopUserServices:
    @pytest.mark.unit
    def test_no_services(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.db.models.ServiceModel.objects.all",
            return_value=[],
        )
        destroy_module._stop_user_services()

    @pytest.mark.unit
    def test_stops_services_with_containers(self, mocker: MockerFixture) -> None:
        svc1 = mocker.MagicMock(container_id="c1", name="svc1")
        svc2 = mocker.MagicMock(container_id=None, name="svc2")
        svc3 = mocker.MagicMock(container_id="c3", name="svc3")
        mocker.patch(
            "svs_core.db.models.ServiceModel.objects.all",
            return_value=[svc1, svc2, svc3],
        )
        mock_run = mocker.patch("subprocess.run")

        destroy_module._stop_user_services()

        assert mock_run.call_count == 2
        calls = [args[0][0] for args in mock_run.call_args_list]
        assert any("c1" in c for c in calls)
        assert any("c3" in c for c in calls)


class TestStopSystemStack:
    @pytest.mark.unit
    def test_no_compose_file(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=False)
        destroy_module._stop_system_stack()

    @pytest.mark.unit
    def test_stops_stack_successfully(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=True)
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0, stderr="")

        destroy_module._stop_system_stack()

        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert "docker" in args
        assert "compose" in args
        assert "down" in args

    @pytest.mark.unit
    def test_stop_failure(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=True)
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=1, stderr="error")

        destroy_module._stop_system_stack()


class TestRemoveVolumes:
    @pytest.mark.unit
    def test_skips_when_keep_volumes(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        destroy_module._remove_volumes(keep_volumes=True)
        mock_run.assert_not_called()

    @pytest.mark.unit
    def test_removes_volumes(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")

        destroy_module._remove_volumes(keep_volumes=False)

        assert mock_run.call_count == 3
        for call_args in mock_run.call_args_list:
            args = call_args[0][0]
            assert "volume" in args
            assert "rm" in args


class TestRemoveConfigDirs:
    @pytest.mark.unit
    def test_removes_directories(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.cli.destroy.os.path.exists", side_effect=[True, True, False]
        )
        mock_rmtree = mocker.patch("svs_core.cli.destroy.shutil.rmtree")

        destroy_module._remove_config_dirs()

        assert mock_rmtree.call_count == 2

    @pytest.mark.unit
    def test_skips_missing_dirs(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=False)
        mock_rmtree = mocker.patch("svs_core.cli.destroy.shutil.rmtree")

        destroy_module._remove_config_dirs()

        mock_rmtree.assert_not_called()

    @pytest.mark.unit
    def test_removes_log_file(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.cli.destroy.os.path.exists", side_effect=[False, False, True]
        )
        mock_remove = mocker.patch("svs_core.cli.destroy.os.remove")

        destroy_module._remove_config_dirs()

        mock_remove.assert_called_once_with("/etc/svs/svs.log")


class TestCleanSudoers:
    @pytest.mark.unit
    def test_no_sudoers_file(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=False)
        destroy_module._clean_sudoers()

    @pytest.mark.unit
    def test_removes_svs_entries(self, mocker: MockerFixture, tmp_path: Path) -> None:
        sudoers = tmp_path / "sudoers"
        sudoers.write_text(
            "# SVS begin\n"
            "ALL ALL=NOPASSWD: /usr/local/bin/svs\n"
            "%svs-admins ALL=(svs) NOPASSWD: /usr/local/bin/svs\n"
            "# SVS end\n"
            "root ALL=(ALL) ALL\n"
        )
        mocker.patch.object(
            destroy_module, "SVS_CONFIG_DIR", str(tmp_path / "etc" / "svs")
        )

        original_exists = os.path.exists

        def mock_exists(path: str) -> bool:
            if path == "/etc/sudoers":
                return True
            return bool(original_exists(path))

        mocker.patch("svs_core.cli.destroy.os.path.exists", side_effect=mock_exists)
        mocker.patch(
            "svs_core.cli.destroy.open",
            mocker.mock_open(read_data=sudoers.read_text()),
        )
        mock_copy2 = mocker.patch("svs_core.cli.destroy.shutil.copy2")

        destroy_module._clean_sudoers()

        mock_copy2.assert_called_once()

    @pytest.mark.unit
    def test_no_svs_entries(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=True)
        mocker.patch(
            "svs_core.cli.destroy.open",
            mocker.mock_open(read_data="root ALL=(ALL) ALL\n"),
        )

        destroy_module._clean_sudoers()

    @pytest.mark.unit
    def test_permission_error_read(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.destroy.os.path.exists", return_value=True)
        mocker.patch(
            "svs_core.cli.destroy.open",
            side_effect=PermissionError("Permission denied"),
        )

        destroy_module._clean_sudoers()


class TestRemoveSystemUser:
    @pytest.mark.unit
    def test_removes_user_and_group(self, mocker: MockerFixture) -> None:
        mock_pwd = mocker.patch("pwd.getpwnam", return_value=True)
        mock_grp = mocker.patch("grp.getgrnam", return_value=True)
        mock_run = mocker.patch("subprocess.run")

        destroy_module._remove_system_user()

        assert mock_run.call_count == 2

    @pytest.mark.unit
    def test_user_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("pwd.getpwnam", side_effect=KeyError("user not found"))
        mock_grp = mocker.patch("grp.getgrnam", return_value=True)
        mock_run = mocker.patch("subprocess.run")

        destroy_module._remove_system_user()

        assert mock_run.call_count == 1

    @pytest.mark.unit
    def test_group_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("pwd.getpwnam", return_value=True)
        mocker.patch("grp.getgrnam", side_effect=KeyError("group not found"))
        mock_run = mocker.patch("subprocess.run")

        destroy_module._remove_system_user()

        assert mock_run.call_count == 1


class TestUninstallPipxPackage:
    @pytest.mark.unit
    def test_uninstall_success(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0, stderr="")

        destroy_module._uninstall_pipx_package()

    @pytest.mark.unit
    def test_uninstall_failure(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=1, stderr="not installed")

        destroy_module._uninstall_pipx_package()


class TestDestroyCmd:
    @pytest.mark.unit
    def test_help_flag(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(app, ["destroy", "--help"])
        assert result.exit_code == 0
        assert "Destroy the SVS environment" in result.output

    @pytest.mark.unit
    def test_destroy_aborts_without_confirmation(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(app, ["destroy"], input="n\n")
        assert result.exit_code == 0
        assert "Aborted" in result.output

    @pytest.mark.unit
    def test_destroy_with_yes_flag(
        self, mocker: MockerFixture, cli_runner: CliRunner
    ) -> None:
        """Should skip confirmation with --yes flag."""
        mocker.patch("svs_core.cli.destroy._stop_user_services")
        mocker.patch("svs_core.cli.destroy._stop_system_stack")
        mocker.patch("svs_core.cli.destroy._remove_volumes")
        mocker.patch("svs_core.cli.destroy._remove_config_dirs")
        mocker.patch("svs_core.cli.destroy._clean_sudoers")
        mocker.patch("svs_core.cli.destroy._remove_system_user")

        result = cli_runner.invoke(app, ["destroy", "--yes"])

        assert result.exit_code == 0
        assert "destroyed" in result.output
