"""Unit tests for svs_core.cli.web module."""

from __future__ import annotations

from pathlib import Path

import pytest
import typer

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app
from svs_core.cli import web as web_module


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


class TestCheckPrerequisites:
    @pytest.mark.unit
    def test_all_found(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)

        web_module._check_prerequisites()

        assert mock_run.call_count == 3

    @pytest.mark.unit
    def test_missing(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=1)

        with pytest.raises(typer.Exit):
            web_module._check_prerequisites()


class TestCreateInstallDir:
    @pytest.mark.unit
    def test_creates_new_dir(self, tmp_path: Path) -> None:
        target = tmp_path / "new_dir"
        assert not target.exists()

        web_module._create_install_dir(target)

        assert target.is_dir()

    @pytest.mark.unit
    def test_uses_existing_dir(self, tmp_path: Path) -> None:
        target = tmp_path / "existing"
        target.mkdir()

        web_module._create_install_dir(target)

        assert target.is_dir()

    @pytest.mark.unit
    def test_fails_on_file_path(self, tmp_path: Path) -> None:
        target = tmp_path / "file"
        target.write_text("not a dir")

        with pytest.raises(typer.Exit):
            web_module._create_install_dir(target)


class TestCloneRepo:
    @pytest.mark.unit
    def test_web_files_already_present(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        (tmp_path / "manage.py").write_text("exists")
        mock_run = mocker.patch("svs_core.cli.web.subprocess.run")

        web_module._clone_repo(tmp_path, "1.0.0")

        mock_run.assert_not_called()

    @pytest.mark.unit
    def test_clones_repo(self, mocker: MockerFixture, tmp_path: Path) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)
        # Create the web dir structure that the move step expects
        (tmp_path / "svs-core" / "web").mkdir(parents=True)
        (tmp_path / "svs-core" / "web" / "manage.py").write_text("")

        web_module._clone_repo(tmp_path, "1.0.0")

        clone_call = mock_run.call_args_list[0]
        args = clone_call[0][0]
        assert "git" in args
        assert "clone" in args
        assert "v1.0.0" in args or "1.0.0" in args
        # Verify files were moved from svs-core/web/ to install_path
        assert (tmp_path / "manage.py").exists()

    @pytest.mark.unit
    def test_fallback_to_default_branch(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_run = mocker.patch("subprocess.run")
        # First clone fails (tag not found), second fails too,
        # third (default branch) succeeds
        mock_run.side_effect = [
            mocker.MagicMock(returncode=1, stderr="not found"),
            mocker.MagicMock(returncode=1, stderr="not found"),
            mocker.MagicMock(returncode=0),
        ]

        web_module._clone_repo(tmp_path, "2.0.0")

        assert mock_run.call_count == 3


class TestSetupVenv:
    @pytest.mark.unit
    def test_creates_venv(self, mocker: MockerFixture, tmp_path: Path) -> None:
        (tmp_path / "requirements.txt").write_text("django\n")
        mock_run = mocker.patch("subprocess.run")

        web_module._setup_venv(tmp_path, "1.0.0")

        venv_calls = [call for call in mock_run.call_args_list if "venv" in str(call)]
        assert len(venv_calls) >= 1

    @pytest.mark.unit
    def test_reuses_existing_venv(self, mocker: MockerFixture, tmp_path: Path) -> None:
        venv_path = tmp_path / ".venv" / "bin"
        venv_path.mkdir(parents=True)
        (venv_path / "python").write_text("")
        mock_run = mocker.patch("subprocess.run")

        web_module._setup_venv(tmp_path, "1.0.0")


class TestBuildFrontend:
    @pytest.mark.unit
    def test_skips_without_package_json(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_run = mocker.patch("subprocess.run")

        web_module._build_frontend(tmp_path)

        mock_run.assert_not_called()

    @pytest.mark.unit
    def test_builds_successfully(self, mocker: MockerFixture, tmp_path: Path) -> None:
        frontend_dir = tmp_path / "frontend"
        frontend_dir.mkdir(parents=True)
        (frontend_dir / "package.json").write_text("{}")
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0)

        web_module._build_frontend(tmp_path)

        assert mock_run.call_count >= 2


class TestConfigureEnv:
    @pytest.mark.unit
    def test_skips_existing_env(self, tmp_path: Path) -> None:
        (tmp_path / ".env").write_text("EXISTING=1")
        web_module._configure_env(tmp_path, "1.0.0", yes=True, domain=None)

        assert (tmp_path / ".env").read_text() == "EXISTING=1"

    @pytest.mark.unit
    def test_creates_from_example(self, mocker: MockerFixture, tmp_path: Path) -> None:
        (tmp_path / ".env.example").write_text("EXAMPLE=1\n")

        web_module._configure_env(tmp_path, "1.0.0", yes=True, domain=None)

        assert (tmp_path / ".env").exists()
        assert "EXAMPLE=1" in (tmp_path / ".env").read_text()

    @pytest.mark.unit
    def test_creates_minimal_when_no_example(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_minimal = mocker.patch("svs_core.cli.web._write_minimal_env")

        web_module._configure_env(tmp_path, "1.0.0", yes=True, domain=None)

        mock_minimal.assert_called_once()


class TestWriteMinimalEnv:
    @pytest.mark.unit
    def test_writes_secret_key(self, tmp_path: Path) -> None:
        env_path = tmp_path / ".env"

        web_module._write_minimal_env(env_path, domain=None)

        content = env_path.read_text()
        assert "DJANGO_SECRET_KEY" in content
        assert "DJANGO_DEBUG=False" in content
        assert "DJANGO_ALLOWED_HOSTS" in content

    @pytest.mark.unit
    def test_includes_domain(self, tmp_path: Path) -> None:
        env_path = tmp_path / ".env"

        web_module._write_minimal_env(env_path, domain="example.com")  # noqa: SC200

        content = env_path.read_text()
        assert "example.com" in content
        assert "CSRF_TRUSTED_ORIGINS" in content

    @pytest.mark.unit
    def test_sets_restrictive_permissions(self, tmp_path: Path) -> None:
        env_path = tmp_path / ".env"

        web_module._write_minimal_env(env_path, domain=None)

        perms = env_path.stat().st_mode & 0o777
        assert perms == 0o600


class TestCollectStatic:
    @pytest.mark.unit
    def test_skips_without_manage_py(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mock_run = mocker.patch("subprocess.run")

        web_module._collect_static(tmp_path)

        mock_run.assert_not_called()

    @pytest.mark.unit
    def test_collects_static(self, mocker: MockerFixture, tmp_path: Path) -> None:
        (tmp_path / "manage.py").write_text("")
        (tmp_path / ".venv" / "bin" / "python").parent.mkdir(parents=True)
        (tmp_path / ".venv" / "bin" / "python").write_text("")
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=0, stderr="")

        web_module._collect_static(tmp_path)

        # Should have a call with collectstatic
        static_calls = [
            call for call in mock_run.call_args_list if "collectstatic" in str(call)
        ]
        assert len(static_calls) >= 1


class TestCreateSystemdService:
    @pytest.mark.unit
    def test_creates_service_file(self, mocker: MockerFixture, tmp_path: Path) -> None:
        venv_python = tmp_path / ".venv" / "bin" / "python"
        venv_python.parent.mkdir(parents=True)
        venv_python.write_text("")

        mocker.patch("pathlib.Path.exists", return_value=False)
        mock_write = mocker.patch("pathlib.Path.write_text")
        mock_chmod = mocker.patch("pathlib.Path.chmod")
        mock_reload = mocker.patch("subprocess.run")

        web_module._create_systemd_service(tmp_path)

        mock_write.assert_called_once()
        mock_chmod.assert_called_once_with(0o644)
        # systemctl daemon-reload should be called
        reload_calls = [
            call for call in mock_reload.call_args_list if "daemon-reload" in str(call)
        ]
        assert len(reload_calls) == 1


class TestWebInitCmd:
    @pytest.mark.unit
    def test_help_flag(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(app, ["web", "init", "--help"])
        assert result.exit_code == 0
        assert "Set up the SVS web interface" in result.output

    @pytest.mark.unit
    def test_version_check_fails(
        self, mocker: MockerFixture, cli_runner: CliRunner
    ) -> None:
        mocker.patch("svs_core.cli.web.version", side_effect=Exception("not found"))

        result = cli_runner.invoke(app, ["web", "init", "--yes"])

        assert result.exit_code != 0
        assert "Could not determine" in result.output
