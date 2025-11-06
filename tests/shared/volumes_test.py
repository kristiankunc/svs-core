import pytest

from svs_core.shared.volumes import SystemVolumeManager


class TestSystemVolumeManager:
    @pytest.fixture(autouse=True)
    def _mock_base_path(self, mocker, tmp_path):
        mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.BASE_PATH", tmp_path
        )

    def test_generate_free_volume(self, svs_user):
        """Test generating a free volume for a user."""
        volume = SystemVolumeManager.generate_free_volume(svs_user)

        assert volume.user == svs_user.name
        assert volume.path.exists()

        # assert permissions are set correctly (rwx------)
        mode = volume.path.stat().st_mode & 0o777
        assert mode == 0o700
