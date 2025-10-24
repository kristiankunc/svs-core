import os
import subprocess

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from svs_core.shared.env_manager import EnvManager
from svs_core.shared.shell import run_command


@pytest.fixture(autouse=True)
def reset_env_manager():
    """Reset EnvManager state before each test."""
    EnvManager._env_loaded = False
    EnvManager._env_vars = {}
    yield
    EnvManager._env_loaded = False
    EnvManager._env_vars = {}


class TestEnvManager:
    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.run_command")
    def test_open_env_file_success(self, mock_run_command):
        """Test successful reading of .env file with comments and empty
        lines."""
        mock_result = MagicMock()
        mock_result.stdout = (
            "# Comment\n"
            "RUNTIME_ENVIRONMENT=development\n"
            "\n"
            "DATABASE_URL=postgres://user:pass=123@localhost\n"
        )
        mock_run_command.return_value = mock_result

        result = EnvManager._open_env_file(Path("/test/.env"))

        assert result == {
            "RUNTIME_ENVIRONMENT": "development",
            "DATABASE_URL": "postgres://user:pass=123@localhost",
        }

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.run_command")
    def test_open_env_file_returns_empty_dict_on_none_result(self, mock_run_command):
        """Test that an empty dict is returned when run_command returns
        None."""
        mock_run_command.return_value = None

        result = EnvManager._open_env_file(Path("/test/.env"))

        assert result == {}

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.run_command")
    def test_open_env_file_raises_on_command_error(self, mock_run_command):
        """Test that FileNotFoundError is raised when command fails."""
        mock_run_command.side_effect = subprocess.CalledProcessError(1, "cat")

        with pytest.raises(FileNotFoundError):
            EnvManager._open_env_file(Path("/test/.env"))

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._open_env_file")
    @patch.dict(os.environ, {}, clear=True)
    def test_load_env_success(self, mock_open_env_file):
        """Test successful loading and merging of environment variables."""
        mock_open_env_file.return_value = {
            "RUNTIME_ENVIRONMENT": "development",
            "DATABASE_URL": "postgres://localhost",
        }

        EnvManager._load_env()

        assert EnvManager._env_loaded is True
        assert EnvManager._env_vars == {
            "RUNTIME_ENVIRONMENT": "development",
            "DATABASE_URL": "postgres://localhost",
        }

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._open_env_file")
    def test_load_env_os_environ_takes_precedence(self, mock_open_env_file):
        """Test that os.environ takes precedence over .env file."""
        mock_open_env_file.return_value = {
            "RUNTIME_ENVIRONMENT": "development",
            "DATABASE_URL": "postgres://localhost",
        }

        with patch.dict(os.environ, {"RUNTIME_ENVIRONMENT": "production"}, clear=True):
            EnvManager._load_env()

            assert EnvManager._env_vars["RUNTIME_ENVIRONMENT"] == "production"
            assert EnvManager._env_vars["DATABASE_URL"] == "postgres://localhost"

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._open_env_file")
    def test_load_env_file_not_found(self, mock_open_env_file):
        """Test that _env_loaded is True even if file not found."""
        mock_open_env_file.side_effect = FileNotFoundError("Not found")

        EnvManager._load_env()

        assert EnvManager._env_loaded is True

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._load_env")
    def test_get_runtime_environment_values(self, mock_load_env):
        """Test getting different runtime environments."""
        EnvManager._env_loaded = True

        test_cases = [
            ("development", EnvManager.RuntimeEnvironment.DEVELOPMENT),
            ("testing", EnvManager.RuntimeEnvironment.TESTING),
            ("production", EnvManager.RuntimeEnvironment.PRODUCTION),
        ]

        for env_value, expected in test_cases:
            EnvManager._env_vars = {"RUNTIME_ENVIRONMENT": env_value}
            assert EnvManager.get_runtime_environment() == expected

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._load_env")
    def test_get_runtime_environment_defaults_to_production(self, mock_load_env):
        """Test that runtime environment defaults to PRODUCTION if not set."""
        EnvManager._env_loaded = True
        EnvManager._env_vars = {}

        result = EnvManager.get_runtime_environment()

        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._load_env")
    def test_get_database_url(self, mock_load_env):
        """Test getting DATABASE_URL when set and when not set."""
        EnvManager._env_loaded = True

        # Test when set
        EnvManager._env_vars = {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        assert EnvManager.get_database_url() == "postgres://user:pass@localhost/db"

        # Test when not set
        EnvManager._env_vars = {}
        assert EnvManager.get_database_url() is None

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.EnvManager._load_env")
    def test_get_calls_load_env_on_first_call(self, mock_load_env):
        """Test that _get calls _load_env on first call but not on subsequent
        calls."""

        def set_loaded():
            EnvManager._env_loaded = True
            EnvManager._env_vars = {"RUNTIME_ENVIRONMENT": "development"}

        EnvManager._env_loaded = False
        EnvManager._env_vars = {}
        mock_load_env.side_effect = set_loaded

        # First call should trigger _load_env
        result1 = EnvManager._get(EnvManager.EnvVarKeys.RUNTIME_ENVIRONMENT)
        assert mock_load_env.call_count == 1

        # Second call should not
        result2 = EnvManager._get(EnvManager.EnvVarKeys.DATABASE_URL)
        assert mock_load_env.call_count == 1

    @pytest.mark.unit
    @patch("svs_core.shared.env_manager.run_command")
    def test_integration_full_env_loading_flow(self, mock_run_command):
        """Test the full flow of loading and retrieving environment
        variables."""
        EnvManager._env_loaded = False
        EnvManager._env_vars = {}

        mock_result = MagicMock()
        mock_result.stdout = (
            "RUNTIME_ENVIRONMENT=development\n"
            "DATABASE_URL=postgres://localhost/testdb"
        )
        mock_run_command.return_value = mock_result

        with patch.dict(os.environ, {}, clear=True):
            runtime_env = EnvManager.get_runtime_environment()
            db_url = EnvManager.get_database_url()

            assert runtime_env == EnvManager.RuntimeEnvironment.DEVELOPMENT
            assert db_url == "postgres://localhost/testdb"
