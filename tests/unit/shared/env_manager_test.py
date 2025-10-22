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
def test_runtime_environment_unknown_value_logs_and_defaults(tmp_path, capsys):
    """Unknown value logs a warning and defaults to DEVELOPMENT."""
    reset_env_manager()
    env_file = tmp_path / ".env"
    env_file.write_text("RUNTIME_ENVIRONMENT=weird\n")
    EnvManager.ENV_FILE_PATH = env_file

    result = EnvManager.get_runtime_environment()
    captured = capsys.readouterr()

    assert result == EnvManager.RuntimeEnvironment.DEVELOPMENT
    assert "Unknown environment" in captured.out


@pytest.mark.unit
def test_read_env_missing_file_raises(tmp_path):
    """Trying to read a non-existent env file should raise
    FileNotFoundError."""
    reset_env_manager()
    EnvManager.ENV_FILE_PATH = tmp_path / "does_not_exist.env"

    with pytest.raises(FileNotFoundError):
        EnvManager._read_env()
