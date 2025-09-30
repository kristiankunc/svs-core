from pathlib import Path

from pytest_mock import MockerFixture

from svs_core.shared.volumes import SystemVolumeManager


class TestSystemVolumeManager:
    def test_generate_free_volume_returns_path(self, tmp_path: Path) -> None:
        """Test that generate_free_volume returns a valid Path object."""
        user_id = 13
        original_base_path = SystemVolumeManager.BASE_PATH
        try:
            SystemVolumeManager.BASE_PATH = tmp_path

            volume_path = SystemVolumeManager.generate_free_volume(user_id)
            assert volume_path.is_absolute()
            assert volume_path.parent == SystemVolumeManager.BASE_PATH / str(user_id)

            volume_path.rmdir()
        finally:
            SystemVolumeManager.BASE_PATH = original_base_path


def test_generate_free_volume_handles_existing_paths(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    """Test that generate_free_volume retries if the generated path already
    exists."""
    user_id = 42
    SystemVolumeManager.BASE_PATH = tmp_path

    volume_id = "a" * 16
    existing_path = tmp_path / str(user_id) / volume_id
    existing_path.mkdir(parents=True, exist_ok=True)

    mocker.patch("random.choice", return_value="a")

    try:
        import pytest

        with pytest.raises(RuntimeError):
            SystemVolumeManager.generate_free_volume(user_id)
    finally:
        SystemVolumeManager.BASE_PATH = Path("/var/svs/volumes")
