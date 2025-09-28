from pathlib import Path
from sys import platform

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
            if platform.startswith("win"):
                expected_parent = SystemVolumeManager.BASE_PATH / str(user_id)
                assert volume_path.parent == expected_parent
            else:
                assert volume_path.parent == SystemVolumeManager.BASE_PATH / str(
                    user_id
                )

            volume_path.rmdir()
        finally:
            SystemVolumeManager.BASE_PATH = original_base_path
