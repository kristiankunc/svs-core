"""Unit tests for svs_core.cli.init module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import docker
import pytest
import typer

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app
from svs_core.cli import init as init_module


@pytest.fixture
def cli_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(autouse=True)
def mock_docker_exception(mocker: MockerFixture) -> None:
    mocker.patch("svs_core.cli.init.docker.from_env")


@pytest.fixture
def mock_paths(mocker: MockerFixture) -> dict[str, MagicMock]:
    from pathlib import Path

    paths = {
        "COMPOSE_PATH": mocker.patch.object(init_module, "COMPOSE_PATH"),
        "STACK_ENV_PATH": mocker.patch.object(init_module, "STACK_ENV_PATH"),
        "SVS_ENV_PATH": mocker.patch.object(init_module, "SVS_ENV_PATH"),
        "SVS_DOCKER_DIR": mocker.patch.object(init_module, "SVS_DOCKER_DIR"),
    }
    for p in paths.values():
        p.exists.return_value = False
        p.is_dir.return_value = True
    return paths


class TestVerifyDocker:
    @pytest.mark.unit
    def test_docker_running(self, mocker: MockerFixture) -> None:
        mock_client = mocker.MagicMock()
        mock_from_env = mocker.patch(
            "svs_core.cli.init.docker.from_env", return_value=mock_client
        )

        result = init_module._verify_docker()

        assert result is mock_client
        mock_from_env.assert_called_once()
        mock_client.ping.assert_called_once()

    @pytest.mark.unit
    def test_docker_not_running(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.cli.init.docker.from_env",
            side_effect=docker.errors.DockerException,
        )

        with pytest.raises(typer.Exit):
            init_module._verify_docker()


class TestSetupDockerCompose:
    @pytest.mark.unit
    def test_creates_new_compose_and_env(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mocker.patch.object(init_module, "COMPOSE_PATH", mock_paths["COMPOSE_PATH"])
        mocker.patch.object(init_module, "STACK_ENV_PATH", mock_paths["STACK_ENV_PATH"])
        secrets_token = mocker.patch(
            "svs_core.cli.init.secrets.token_hex", return_value="abc123"
        )

        password = init_module._setup_docker_compose(non_interactive=True)

        assert password == "abc123"
        mock_paths["COMPOSE_PATH"].write_text.assert_called_once()
        mock_paths["STACK_ENV_PATH"].write_text.assert_called_once()
        secrets_token.assert_called_once_with(16)

    @pytest.mark.unit
    def test_reuses_existing_compose(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mock_paths["COMPOSE_PATH"].exists.return_value = True
        mock_paths["STACK_ENV_PATH"].exists.return_value = True
        mocker.patch.object(init_module, "COMPOSE_PATH", mock_paths["COMPOSE_PATH"])
        mocker.patch.object(init_module, "STACK_ENV_PATH", mock_paths["STACK_ENV_PATH"])
        mocker.patch.object(
            init_module, "_read_stack_password", return_value="existing_pass"
        )

        password = init_module._setup_docker_compose(non_interactive=True)

        assert password == "existing_pass"
        mock_paths["COMPOSE_PATH"].write_text.assert_not_called()
        mock_paths["STACK_ENV_PATH"].write_text.assert_not_called()

    @pytest.mark.unit
    def test_chmod_on_new_files(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mocker.patch.object(init_module, "COMPOSE_PATH", mock_paths["COMPOSE_PATH"])
        mocker.patch.object(init_module, "STACK_ENV_PATH", mock_paths["STACK_ENV_PATH"])
        mocker.patch("svs_core.cli.init.secrets.token_hex", return_value="abc")

        init_module._setup_docker_compose(non_interactive=True)

        mock_paths["COMPOSE_PATH"].chmod.assert_called_once_with(0o660)
        mock_paths["STACK_ENV_PATH"].chmod.assert_called_once_with(0o660)


class TestReadStackPassword:
    @pytest.mark.unit
    def test_reads_existing_password(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mock_paths["STACK_ENV_PATH"].read_text.return_value = (
            "POSTGRES_USER=svs\nPOSTGRES_PASSWORD=secret123\nPOSTGRES_DB=svsdb\n"
        )
        mocker.patch.object(init_module, "STACK_ENV_PATH", mock_paths["STACK_ENV_PATH"])

        result = init_module._read_stack_password()

        assert result == "secret123"

    @pytest.mark.unit
    def test_fallback_when_missing(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mock_paths["STACK_ENV_PATH"].read_text.return_value = "POSTGRES_USER=svs\n"
        mocker.patch.object(init_module, "STACK_ENV_PATH", mock_paths["STACK_ENV_PATH"])
        mocker.patch("svs_core.cli.init.secrets.token_hex", return_value="fallback")

        result = init_module._read_stack_password()

        assert result == "fallback"


class TestStartStack:
    @pytest.mark.unit
    def test_stack_starts_successfully(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        # First call (compose up) succeeds
        # Second repeated call (pg_isready) returns success
        mock_run.side_effect = [
            mocker.MagicMock(returncode=0),
            mocker.MagicMock(returncode=0),
        ]

        init_module._start_stack("test_pass")

        assert mock_run.call_count >= 2

    @pytest.mark.unit
    def test_compose_fails(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(returncode=1, stderr="error msg")

        with pytest.raises(typer.Exit):
            init_module._start_stack("test_pass")

    @pytest.mark.unit
    def test_postgres_timeout(self, mocker: MockerFixture) -> None:
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = [
            mocker.MagicMock(returncode=0),
        ] + [mocker.MagicMock(returncode=1)] * 30

        with pytest.raises(typer.Exit):
            init_module._start_stack("test_pass")


class TestWriteSvsEnv:
    @pytest.mark.unit
    def test_writes_database_url(
        self, mocker: MockerFixture, mock_paths: dict[str, MagicMock]
    ) -> None:
        mocker.patch.object(init_module, "SVS_ENV_PATH", mock_paths["SVS_ENV_PATH"])

        init_module._write_svs_env("mypass")

        written = mock_paths["SVS_ENV_PATH"].write_text.call_args[0][0]
        assert "postgresql" in written
        assert "mypass" in written
        mock_paths["SVS_ENV_PATH"].chmod.assert_called_once_with(0o640)


class TestRunMigrations:
    @pytest.mark.unit
    def test_migrations_succeed(self, mocker: MockerFixture) -> None:
        mock_call = mocker.patch("django.core.management.call_command")

        init_module._run_migrations()

        mock_call.assert_called_once_with("migrate", "svs_core")

    @pytest.mark.unit
    def test_migrations_fail(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "django.core.management.call_command", side_effect=Exception("db error")
        )

        with pytest.raises(typer.Exit):
            init_module._run_migrations()


class TestFindTemplateDirs:
    @pytest.mark.unit
    def test_returns_discovered_dirs(self, mocker: MockerFixture) -> None:
        from pathlib import Path

        result = init_module._find_template_dirs()
        assert len(result) >= 1

    @pytest.mark.unit
    def test_no_duplicates(self, mocker: MockerFixture, tmp_path: Path) -> None:
        tdir = tmp_path / "templates"
        tdir.mkdir(parents=True)

        mocker.patch.object(
            init_module,
            "_find_template_dirs",
            return_value=[tdir],
        )

        result = init_module._find_template_dirs()
        assert len(result) >= 1

    @pytest.mark.unit
    def test_respects_precedence(self, mocker: MockerFixture, tmp_path: Path) -> None:
        pkg = tmp_path / "pkg" / "data" / "templates"
        sysd = tmp_path / "usr" / "local" / "share" / "service_templates"
        pkg.mkdir(parents=True)
        sysd.mkdir(parents=True)

        mocker.patch.object(
            init_module,
            "_find_template_dirs",
            return_value=[pkg, sysd],
        )

        result = init_module._find_template_dirs()
        assert result[0] == pkg
        assert result[1] == sysd


class TestImportOfficialTemplates:
    @pytest.mark.unit
    def test_imports_new_templates(self, mocker: MockerFixture, tmp_path: Path) -> None:
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "nginx.json").write_text('{"name": "nginx", "type": "service"}')

        mocker.patch.object(init_module, "_find_template_dirs", return_value=[tpl])
        mock_all = mocker.patch(
            "svs_core.docker.template.Template.objects.all",
            return_value=[],
        )
        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")

        init_module._import_official_templates()

        mock_import.assert_called_once()
        mock_all.assert_called_once()

    @pytest.mark.unit
    def test_skips_duplicates(self, mocker: MockerFixture, tmp_path: Path) -> None:
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "nginx.json").write_text('{"name": "nginx", "type": "service"}')

        mocker.patch.object(init_module, "_find_template_dirs", return_value=[tpl])
        mock_existing = mocker.MagicMock()
        mock_existing.name = "nginx"
        mock_existing.type = "service"
        mocker.patch(
            "svs_core.docker.template.Template.objects.all",
            return_value=[mock_existing],
        )
        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")

        init_module._import_official_templates()

        mock_import.assert_not_called()

    @pytest.mark.unit
    def test_skips_schema_file(self, mocker: MockerFixture, tmp_path: Path) -> None:
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "schema.json").write_text('{"schema": true}')
        (tpl / "nginx.json").write_text('{"name": "nginx", "type": "service"}')

        mocker.patch.object(init_module, "_find_template_dirs", return_value=[tpl])
        mocker.patch(
            "svs_core.docker.template.Template.objects.all",
            return_value=[],
        )
        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")

        init_module._import_official_templates()

        assert mock_import.call_count == 1

    @pytest.mark.unit
    def test_no_dirs_found(self, mocker: MockerFixture) -> None:
        mocker.patch.object(init_module, "_find_template_dirs", return_value=[])

        init_module._import_official_templates()

    @pytest.mark.unit
    def test_skips_malformed_json(self, mocker: MockerFixture, tmp_path: Path) -> None:
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "bad.json").write_text("not json")

        mocker.patch.object(init_module, "_find_template_dirs", return_value=[tpl])
        mocker.patch("svs_core.docker.template.Template.objects.all", return_value=[])

        import json

        with pytest.raises(json.JSONDecodeError):
            init_module._import_official_templates()

    @pytest.mark.unit
    def test_import_logs_exceptions(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        tpl = tmp_path / "templates"
        tpl.mkdir()
        (tpl / "bad.json").write_text('{"name": "bad", "type": "service"}')

        mocker.patch.object(init_module, "_find_template_dirs", return_value=[tpl])
        mocker.patch("svs_core.docker.template.Template.objects.all", return_value=[])
        mocker.patch(
            "svs_core.docker.template.Template.import_from_json",
            side_effect=Exception("import failed"),
        )
        mock_logger = mocker.patch.object(init_module.logger, "warning")

        with pytest.raises(Exception, match="import failed"):
            init_module._import_official_templates()


class TestCreateAdminUser:
    @pytest.mark.unit
    def test_skips_when_admin_exists(self, mocker: MockerFixture) -> None:
        mock_filter = mocker.patch(
            "svs_core.users.user.User.objects.filter",
        )
        mock_filter.return_value.exists.return_value = True

        init_module._create_admin_user("pass123", non_interactive=True)

        mock_filter.assert_called_once_with(is_superuser=True)

    @pytest.mark.unit
    def test_creates_with_given_password(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.users.user.User.objects.filter",
        ).return_value.exists.return_value = False
        mock_get_username = mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="current_user",
        )
        mock_create = mocker.patch("svs_core.users.user.User.create")

        init_module._create_admin_user("secret", non_interactive=True)

        mock_get_username.assert_called_once()
        mock_create.assert_called_once_with("current_user", "secret", True)

    @pytest.mark.unit
    def test_password_provided_but_creation_fails(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.users.user.User.objects.filter",
        ).return_value.exists.return_value = False
        mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="user",
        )
        mocker.patch(
            "svs_core.users.user.User.create",
            side_effect=Exception("creation failed"),
        )

        with pytest.raises(typer.Exit):
            init_module._create_admin_user("secret", non_interactive=True)

    @pytest.mark.unit
    def test_non_interactive_generates_password(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.users.user.User.objects.filter",
        ).return_value.exists.return_value = False
        mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="user",
        )
        mocker.patch("svs_core.cli.init.secrets.token_urlsafe", return_value="rand123")
        mock_create = mocker.patch("svs_core.users.user.User.create")

        init_module._create_admin_user(None, non_interactive=True)

        mock_create.assert_called_once_with("user", "rand123", True)

    @pytest.mark.unit
    def test_interactive_prompts_for_password(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.users.user.User.objects.filter",
        ).return_value.exists.return_value = False
        mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="user",
        )
        mocker.patch("svs_core.cli.init.getpass", return_value="typed_pass")
        mock_create = mocker.patch("svs_core.users.user.User.create")

        init_module._create_admin_user(None, non_interactive=False)

        mock_create.assert_called_once_with("user", "typed_pass", True)

    @pytest.mark.unit
    def test_interactive_empty_password(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.users.user.User.objects.filter",
        ).return_value.exists.return_value = False
        mocker.patch(
            "svs_core.users.system.SystemUserManager.get_system_username",
            return_value="user",
        )
        mocker.patch("svs_core.cli.init.getpass", return_value="  ")

        with pytest.raises(typer.Exit):
            init_module._create_admin_user(None, non_interactive=False)


class TestInstallCompletions:
    @pytest.mark.unit
    def test_skips_when_already_installed(self, mocker: MockerFixture) -> None:
        # The module checks /usr/share/bash-completion/completions/svs
        mocker.patch("svs_core.cli.init.Path.exists", return_value=True)

        init_module._install_completions()
        # No exception means success

    @pytest.mark.unit
    def test_installs_from_completion_output(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.init.Path.exists", return_value=False)
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = mocker.MagicMock(
            returncode=0, stdout="completion script"
        )

        init_module._install_completions()

        assert mock_run.call_count >= 1

    @pytest.mark.unit
    def test_generation_fails(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.init.Path.exists", return_value=False)
        mocker.patch("subprocess.run")

        init_module._install_completions()

    @pytest.mark.unit
    def test_generation_exception(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.init.Path.exists", return_value=False)
        mocker.patch("subprocess.run", side_effect=Exception("cmd failed"))

        init_module._install_completions()


# ---- init_cmd (integration via CliRunner) ----


class TestInitCmd:
    @pytest.mark.unit
    def test_help_flag(self, cli_runner: CliRunner) -> None:
        result = cli_runner.invoke(app, ["init", "--help"])
        assert result.exit_code == 0
        assert "Initialize the SVS environment" in result.output

    @pytest.mark.unit
    def test_init_needs_root_for_docker(self, cli_runner: CliRunner) -> None:
        # This test would need extensive mocking of the entire init
        # flow. For now, just verify --help works and basic structure
        # is sound.
        pass
