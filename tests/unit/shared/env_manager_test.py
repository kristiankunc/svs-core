import os

import pytest

from pytest_mock import MockerFixture

from svs_core.shared.env_manager import EnvManager


class TestEnvManager:
    @pytest.mark.unit
    def test_get_runtime_environment_development(self, mocker: MockerFixture) -> None:
        mocker.patch.dict(os.environ, {"ENVIRONMENT": "development"})
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT

    @pytest.mark.unit
    def test_get_runtime_environment_development_uppercase(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(os.environ, {"ENVIRONMENT": "DEVELOPMENT"})
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT

    @pytest.mark.unit
    def test_get_runtime_environment_production(self, mocker: MockerFixture) -> None:
        mocker.patch.dict(os.environ, {"ENVIRONMENT": "production"})
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    def test_get_runtime_environment_defaults_to_production(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(os.environ, {}, clear=True)
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    def test_get_runtime_environment_empty_string_defaults_to_production(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(os.environ, {"ENVIRONMENT": ""})
        result = EnvManager.get_runtime_environment()
        assert result == EnvManager.RuntimeEnvironment.PRODUCTION

    @pytest.mark.unit
    def test_get_database_url_success(self, mocker: MockerFixture) -> None:
        mocker.patch.dict(
            os.environ, {"DATABASE_URL": "postgres://user:pass@localhost/db"}
        )
        result = EnvManager.get_database_url()
        assert result == "postgres://user:pass@localhost/db"

    @pytest.mark.unit
    def test_get_database_url_not_set_raises_error(self, mocker: MockerFixture) -> None:
        mocker.patch.dict(os.environ, {}, clear=True)
        with pytest.raises(EnvironmentError) as exc_info:
            EnvManager.get_database_url()
        assert "DATABASE_URL environment variable not set" in str(exc_info.value)

    @pytest.mark.unit
    def test_get_database_url_empty_string_raises_error(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch.dict(os.environ, {"DATABASE_URL": ""})
        with pytest.raises(EnvironmentError) as exc_info:
            EnvManager.get_database_url()
        assert "DATABASE_URL environment variable not set" in str(exc_info.value)

    @pytest.mark.unit
    def test_env_variables_enum_members(self) -> None:
        assert hasattr(EnvManager.EnvVariables, "ENVIRONMENT")
        assert hasattr(EnvManager.EnvVariables, "DATABASE_URL")
        assert EnvManager.EnvVariables.ENVIRONMENT.value == "ENVIRONMENT"
        assert EnvManager.EnvVariables.DATABASE_URL.value == "DATABASE_URL"

    @pytest.mark.unit
    def test_runtime_environment_enum_members(self) -> None:
        assert hasattr(EnvManager.RuntimeEnvironment, "DEVELOPMENT")
        assert hasattr(EnvManager.RuntimeEnvironment, "PRODUCTION")
        assert EnvManager.RuntimeEnvironment.DEVELOPMENT.value == "development"
        assert EnvManager.RuntimeEnvironment.PRODUCTION.value == "production"

    @pytest.mark.unit
    def test_get_method(self, mocker: MockerFixture) -> None:
        mock_getenv = mocker.patch("os.getenv", return_value="test_value")
        result = EnvManager._get(EnvManager.EnvVariables.ENVIRONMENT)
        assert result == "test_value"
        mock_getenv.assert_called_once_with("ENVIRONMENT")

    @pytest.mark.unit
    def test_get_method_returns_none_when_not_set(self, mocker: MockerFixture) -> None:
        mock_getenv = mocker.patch("os.getenv", return_value=None)
        result = EnvManager._get(EnvManager.EnvVariables.DATABASE_URL)
        assert result is None
        mock_getenv.assert_called_once_with("DATABASE_URL")
