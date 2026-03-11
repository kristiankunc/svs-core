from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app
from svs_core.migrations.migrator import PackageVersion


@pytest.mark.cli
class TestUtilsCommands:
    """Test suite for utility CLI commands."""

    runner: CliRunner

    def setup_method(self) -> None:
        self.runner = CliRunner()

    # format-dockerfile command tests
    def test_format_dockerfile_file_not_found(self, tmp_path: Path) -> None:
        """Test format-dockerfile with non-existent file."""
        result = self.runner.invoke(
            app,
            ["utils", "format-dockerfile", str(tmp_path / "nonexistent.dockerfile")],
        )

        assert result.exit_code == 1
        assert "does not exist or is not a file" in result.output

    def test_format_dockerfile_successful(self, tmp_path: Path) -> None:
        """Test successful Dockerfile formatting."""
        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text('FROM python:3.13\nRUN echo "Hello"')

        result = self.runner.invoke(
            app,
            ["utils", "format-dockerfile", str(dockerfile)],
        )

        assert result.exit_code == 0
        assert 'FROM python:3.13\\nRUN echo \\"Hello\\"' in result.output

    # django-shell command tests
    def test_django_shell_without_admin(self, mocker: MockerFixture) -> None:
        """Test django-shell without admin rights."""
        mocker.patch(
            "svs_core.cli.utils.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(app, ["utils", "django-shell", "migrate"])

        assert result.exit_code == 1

    def test_django_shell_successful(self, mocker: MockerFixture) -> None:
        """Test successful django-shell execution."""
        mocker.patch("svs_core.cli.utils.reject_if_not_admin")
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")

        result = self.runner.invoke(app, ["utils", "django-shell", "migrate"])

        assert result.exit_code == 0
        assert "Success" in result.output
        mock_run.assert_called_once()

    def test_django_shell_execution_failed(self, mocker: MockerFixture) -> None:
        """Test django-shell when command fails."""
        mocker.patch("svs_core.cli.utils.reject_if_not_admin")
        mock_run = mocker.patch("subprocess.run")
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="Error")

        result = self.runner.invoke(app, ["utils", "django-shell", "migrate"])

        assert result.exit_code == 1
        assert "Error executing Django shell commands" in result.output

    # migrate command tests
    def test_migrate_without_admin(self, mocker: MockerFixture) -> None:
        """Test migrate command without admin rights."""
        mocker.patch(
            "svs_core.cli.utils.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(app, ["utils", "migrate", "0.14.0"])

        assert result.exit_code == 1

    def test_migrate_invalid_version(self, mocker: MockerFixture) -> None:
        """Test migrate with invalid version format."""
        mocker.patch("svs_core.cli.utils.reject_if_not_admin")

        result = self.runner.invoke(app, ["utils", "migrate", "invalid"])

        assert result.exit_code == 1
        assert "Error" in result.output

    def test_migrate_no_migrations_needed(self, mocker: MockerFixture) -> None:
        """Test migrate when no migrations are needed."""
        mocker.patch("svs_core.cli.utils.reject_if_not_admin")
        mock_version = mocker.patch(
            "svs_core.cli.utils.Migrator.get_current_package_version"
        )
        mock_version.return_value = PackageVersion("0.15.0")

        result = self.runner.invoke(app, ["utils", "migrate", "0.15.0"])

        assert result.exit_code == 0
        assert "No migrations needed" in result.output

    def test_migrate_successful(self, mocker: MockerFixture) -> None:
        """Test successful migration."""
        mocker.patch("svs_core.cli.utils.reject_if_not_admin")
        mock_version = mocker.patch(
            "svs_core.cli.utils.Migrator.get_current_package_version"
        )
        mock_version.return_value = PackageVersion("0.15.0")
        mock_run = mocker.patch("svs_core.cli.utils.Migrator.run")

        result = self.runner.invoke(app, ["utils", "migrate", "0.14.0"])

        assert result.exit_code == 0
        assert "Migrations completed successfully" in result.output
        mock_run.assert_called_once()
