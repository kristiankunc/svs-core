import os

from unittest.mock import patch

import pytest

from svs_core.shared.env_manager import EnvManager


class TestEnvManager:
    @pytest.mark.unit
    @patch.dict(os.environ, {"ENVIRONMENT": "development"})
    def test_get_runtime_environment_development(self):
        """Test getting DEVELOPMENT runtime environment."""
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT

    @pytest.mark.unit
    @patch.dict(os.environ, {"ENVIRONMENT": "DEVELOPMENT"})
    def test_get_runtime_environment_development_uppercase(self):
        """Test getting DEVELOPMENT runtime environment with uppercase
        value."""
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT

    @pytest.mark.unit
    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_get_runtime_environment_production(self):
        """Test getting PRODUCTION runtime environment."""
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_get_runtime_environment_defaults_to_production(self):
        """Test that runtime environment defaults to PRODUCTION if not set."""
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    @patch.dict(os.environ, {"ENVIRONMENT": ""})
    def test_get_runtime_environment_empty_string_defaults_to_production(self):
        """Test that empty ENVIRONMENT string defaults to PRODUCTION."""
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    @patch.dict(os.environ, {"DATABASE_URL": "postgres://user:pass@localhost/db"})
    def test_get_database_url_success(self):
        """Test retrieving DATABASE_URL when set."""
        result = EnvManager.get_database_url()
        assert result == "postgres://user:pass@localhost/db"

    @pytest.mark.unit
    @patch.dict(os.environ, {}, clear=True)
    def test_get_database_url_not_set_raises_error(self):
        """Test that EnvironmentError is raised when DATABASE_URL is not
        set."""
        with pytest.raises(EnvironmentError) as exc_info:
            EnvManager.get_database_url()
        assert "DATABASE_URL environment variable not set" in str(exc_info.value)

    @pytest.mark.unit
    @patch.dict(os.environ, {"DATABASE_URL": ""})
    def test_get_database_url_empty_string_raises_error(self):
        """Test that EnvironmentError is raised when DATABASE_URL is empty."""
        with pytest.raises(EnvironmentError) as exc_info:
            EnvManager.get_database_url()
        assert "DATABASE_URL environment variable not set" in str(exc_info.value)

    @pytest.mark.unit
    def test_env_variables_enum_members(self):
        """Test that EnvVariables enum has correct members."""
        assert hasattr(EnvManager.EnvVariables, "ENVIRONMENT")
        assert hasattr(EnvManager.EnvVariables, "DATABASE_URL")
        assert EnvManager.EnvVariables.ENVIRONMENT.value == "ENVIRONMENT"
        assert EnvManager.EnvVariables.DATABASE_URL.value == "DATABASE_URL"

    @pytest.mark.unit
    def test_runtime_environment_enum_members(self):
        """Test that RuntimeEnvironment enum has correct members."""
        assert hasattr(EnvManager.RuntimeEnvironment, "DEVELOPMENT")
        assert hasattr(EnvManager.RuntimeEnvironment, "PRODUCTION")
        assert EnvManager.RuntimeEnvironment.DEVELOPMENT.value == "development"
        assert EnvManager.RuntimeEnvironment.PRODUCTION.value == "production"

    @pytest.mark.unit
    @patch("os.getenv")
    def test_get_method(self, mock_getenv):
        """Test the _get method retrieves environment variables correctly."""
        mock_getenv.return_value = "test_value"
        result = EnvManager._get(EnvManager.EnvVariables.ENVIRONMENT)
        assert result == "test_value"
        mock_getenv.assert_called_once_with("ENVIRONMENT")

    @pytest.mark.unit
    @patch("os.getenv")
    def test_get_method_returns_none_when_not_set(self, mock_getenv):
        """Test the _get method returns None when variable is not set."""
        mock_getenv.return_value = None
        result = EnvManager._get(EnvManager.EnvVariables.DATABASE_URL)
        assert result is None
        mock_getenv.assert_called_once_with("DATABASE_URL")
