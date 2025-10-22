from pathlib import Path

import pytest

from svs_core.shared.env_manager import EnvManager


def reset_env_manager():
    EnvManager._env_cache_internal = None
    EnvManager._env_cache = None
    EnvManager._env_loaded = False


@pytest.mark.unit
def test_runtime_environment_defaults_to_development(tmp_path):
    """Empty env file -> default to DEVELOPMENT."""
    reset_env_manager()
    env_file = tmp_path / ".env"
    env_file.write_text("")
    EnvManager.ENV_FILE_PATH = env_file

    assert (
        EnvManager.get_runtime_environment()
        == EnvManager.RuntimeEnvironment.DEVELOPMENT
    )


@pytest.mark.unit
def test_runtime_environment_respects_value(tmp_path):
    """RUNTIME_ENVIRONMENT=production -> PRODUCTION."""
    reset_env_manager()
    env_file = tmp_path / ".env"
    env_file.write_text("RUNTIME_ENVIRONMENT=production\n")
    EnvManager.ENV_FILE_PATH = env_file

    assert (
        EnvManager.get_runtime_environment() == EnvManager.RuntimeEnvironment.PRODUCTION
    )


@pytest.mark.unit
def test_runtime_environment_unknown_value_logs_and_defaults(tmp_path):
    """Unknown value defaults to DEVELOPMENT."""
    reset_env_manager()
    env_file = tmp_path / ".env"
    env_file.write_text("RUNTIME_ENVIRONMENT=weird\n")
    EnvManager.ENV_FILE_PATH = env_file

    result = EnvManager.get_runtime_environment()

    assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT


@pytest.mark.unit
def test_read_env_missing_file_raises(tmp_path):
    """Trying to read a non-existent env file should raise
    FileNotFoundError."""
    reset_env_manager()
    EnvManager.ENV_FILE_PATH = tmp_path / "does_not_exist.env"

    with pytest.raises(FileNotFoundError):
        EnvManager._read_env()


@pytest.mark.unit
def test_load_local_dev_env(tmp_path, mocker):
    """Ensure local .env file is loaded in DEVELOPMENT environment."""
    reset_env_manager()

    main_env_file = tmp_path / ".env"
    main_env_file.write_text("RUNTIME_ENVIRONMENT=development\nKEY1=value1\n")
    EnvManager.ENV_FILE_PATH = main_env_file

    local_env_file = tmp_path / "local.env"
    local_env_file.write_text("KEY2=value2\n")

    # Mock the _open_env_file method
    original_open_env_file = EnvManager._open_env_file

    def mock_open_env_file(path):
        if path == Path(".env"):
            return original_open_env_file(local_env_file)
        return original_open_env_file(path)

    mocker.patch(
        "svs_core.shared.env_manager.EnvManager._open_env_file",
        side_effect=mock_open_env_file,
    )

    env_vars = EnvManager._read_env()
    assert env_vars["KEY1"] == "value1"
    assert env_vars["KEY2"] == "value2"
