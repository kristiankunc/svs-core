import pytest

from svs_core.shared.volumes import SystemVolumeManager
from svs_core.users.user import User


class TestVolumes:
    @pytest.mark.unit
    @pytest.mark.django_db
    def test_volume_create(self, tmp_path, mocker):
        """Test creating a volume for a user."""
        mocker.patch("svs_core.shared.volumes.SystemVolumeManager.BASE_PATH", tmp_path)
        mocker.patch(
            "svs_core.users.user.User.create",
            return_value=type("User", (object,), {"id": 1, "name": "testuser"})(),
        )

        user = User.create(name="testuser", password="password123")

        volume_path = SystemVolumeManager.generate_free_volume(user)

        assert volume_path.exists()
        assert volume_path.is_dir()
        assert str(volume_path).startswith(str(tmp_path / str(user.id)))

    @pytest.mark.unit
    @pytest.mark.django_db
    def test_volumue_user_delete(self, tmp_path, mocker):
        """Test deleting volumes for a user."""
        mocker.patch("svs_core.shared.volumes.SystemVolumeManager.BASE_PATH", tmp_path)
        mocker.patch(
            "svs_core.users.user.User.create",
            return_value=type("User", (object,), {"id": 1, "name": "testuser"})(),
        )

        user = User.create(name="testuser", password="password123")

        volume_path = SystemVolumeManager.generate_free_volume(user)
        assert volume_path.exists()

        SystemVolumeManager.delete_user_volumes(user.id)

        user_path = tmp_path / str(user.id)
        assert not user_path.exists()
