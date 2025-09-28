from sys import platform

from svs_core.shared.volumes import SystemVolumeManager


class TestSystemVolumeManager:
    def test_generate_free_volume_returns_path(self):
        """Test that generate_free_volume returns a valid Path object."""

        user_id = "testuser"
        volume_path = SystemVolumeManager.generate_free_volume(user_id)
        print(volume_path)
        assert volume_path.is_absolute()
        if platform.startswith("win"):
            expected_parent = (
                volume_path.drive / SystemVolumeManager.BASE_PATH / user_id
            )
            assert volume_path.parent == expected_parent
        else:
            assert volume_path.parent == SystemVolumeManager.BASE_PATH / user_id

        volume_path.rmdir()
