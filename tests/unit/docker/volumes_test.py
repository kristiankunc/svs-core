from pathlib import Path
from unittest.mock import patch

import pytest

from svs_core.shared.volumes import SystemVolumeManager


@pytest.fixture(autouse=True)
def mock_base_volume_path(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "svs_core.shared.volumes.SystemVolumeManager.BASE_PATH",
        tmp_path / "volumes",
    )


@pytest.fixture
def mock_run_command(mocker):
    return mocker.patch("svs_core.shared.volumes.run_command")


@pytest.fixture
def mock_user(mocker):
    user = mocker.Mock()
    user.id = 123
    user.name = "testuser"
    return user


class TestVolumes:
    @pytest.mark.unit
    def test_generate_free_volume_creates_directory(self, mock_user, mock_run_command):
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.exists()
        assert volume_path.is_dir()
        assert str(mock_user.id) in volume_path.parts
        assert len(volume_path.name) == 16

    @pytest.mark.unit
    def test_generate_free_volume_returns_absolute_path(
        self, mock_user, mock_run_command
    ):
        """Test that generate_free_volume returns an absolute path."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.is_absolute()

    @pytest.mark.unit
    def test_generate_free_volume_generates_unique_paths(
        self, mock_user, mock_run_command
    ):
        """Test that generate_free_volume generates unique paths for multiple
        calls."""
        volume_path1 = SystemVolumeManager.generate_free_volume(mock_user)
        volume_path2 = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path1 != volume_path2
        assert volume_path1.exists()
        assert volume_path2.exists()

    @pytest.mark.unit
    def test_generate_free_volume_creates_nested_directories(
        self, mock_user, mock_run_command
    ):
        """Test that generate_free_volume creates nested user and volume
        directories."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        # Check that the user directory exists
        user_dir = SystemVolumeManager.BASE_PATH / str(mock_user.id)
        assert user_dir.exists()
        assert user_dir.is_dir()

        # Check that the volume is within the user directory
        assert volume_path.parent == user_dir

    @pytest.mark.unit
    def test_delete_user_volumes_removes_all_volumes(
        self, mock_user, tmp_path, mock_run_command
    ):
        """Test that delete_user_volumes removes all volumes for a user."""
        # Create multiple volumes for the user
        SystemVolumeManager.generate_free_volume(mock_user)
        SystemVolumeManager.generate_free_volume(mock_user)

        user_dir = SystemVolumeManager.BASE_PATH / str(mock_user.id)
        assert user_dir.exists()

        # Delete all volumes
        SystemVolumeManager.delete_user_volumes(mock_user.id)

        assert not user_dir.exists()

    @pytest.mark.unit
    def test_delete_user_volumes_removes_files_in_volumes(
        self, mock_user, mock_run_command
    ):
        """Test that delete_user_volumes removes files within volume
        directories."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        # Create a file in the volume
        test_file = volume_path / "test.txt"
        test_file.write_text("test content")

        assert test_file.exists()

        # Delete all volumes
        SystemVolumeManager.delete_user_volumes(mock_user.id)

        assert not volume_path.exists()
        assert not test_file.exists()

    @pytest.mark.unit
    def test_delete_user_volumes_with_nonexistent_user(self):
        # Should not raise an error
        SystemVolumeManager.delete_user_volumes(999)

    @pytest.mark.unit
    def test_delete_user_volumes_removes_only_user_volumes(
        self, mock_user, mocker, mock_run_command
    ):
        """Test that delete_user_volumes only removes volumes for the specific
        user."""
        # Create volumes for mock_user
        SystemVolumeManager.generate_free_volume(mock_user)

        # Create volumes for another user
        other_user = mocker.Mock()
        other_user.id = 456
        other_user.name = "otheruser"
        SystemVolumeManager.generate_free_volume(other_user)

        other_user_dir = SystemVolumeManager.BASE_PATH / str(other_user.id)
        assert other_user_dir.exists()

        # Delete only mock_user's volumes
        SystemVolumeManager.delete_user_volumes(mock_user.id)

        # Check that other user's volumes still exist
        assert other_user_dir.exists()
        assert not (SystemVolumeManager.BASE_PATH / str(mock_user.id)).exists()

    @pytest.mark.unit
    def test_volume_id_has_correct_length(self, mock_user, mock_run_command):
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)
        volume_id = volume_path.name

        assert len(volume_id) == 16
        assert volume_id.isalpha()
        assert volume_id.islower()

    @pytest.mark.unit
    def test_generate_free_volume_with_different_users(self, mocker, mock_run_command):
        user1 = mocker.Mock()
        user1.id = 111
        user1.name = "user1"
        user2 = mocker.Mock()
        user2.id = 222
        user2.name = "user2"

        volume1 = SystemVolumeManager.generate_free_volume(user1)
        volume2 = SystemVolumeManager.generate_free_volume(user2)

        assert str(user1.id) in volume1.parts
        assert str(user2.id) in volume2.parts
        assert volume1.parent.parent == volume2.parent.parent

    @pytest.mark.unit
    def test_delete_volume_removes_specific_volume(self, mock_user, mock_run_command):
        volume_path1 = SystemVolumeManager.generate_free_volume(mock_user)
        volume_path2 = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path1.exists()
        assert volume_path2.exists()

        # Delete only the first volume
        SystemVolumeManager.delete_volume(volume_path1)

        assert not volume_path1.exists()
        assert volume_path2.exists()

    @pytest.mark.unit
    def test_delete_volume_with_files(self, mock_user, mock_run_command):
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        # Create files in the volume
        test_file1 = volume_path / "file1.txt"
        test_file2 = volume_path / "file2.txt"
        test_file1.write_text("content 1")
        test_file2.write_text("content 2")

        assert test_file1.exists()
        assert test_file2.exists()

        # Delete the volume
        SystemVolumeManager.delete_volume(volume_path)

        assert not volume_path.exists()
        assert not test_file1.exists()
        assert not test_file2.exists()

    @pytest.mark.unit
    def test_delete_volume_with_nonexistent_volume(self):
        nonexistent_path = SystemVolumeManager.BASE_PATH / "999" / "nonexistent"

        # Should not raise an error
        SystemVolumeManager.delete_volume(nonexistent_path)

    @pytest.mark.unit
    def test_delete_volume_does_not_affect_other_volumes(
        self, mock_user, mocker, mock_run_command
    ):
        """Test that delete_volume only removes the specified volume."""
        volume_path1 = SystemVolumeManager.generate_free_volume(mock_user)
        volume_path2 = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path1.exists()
        assert volume_path2.exists()

        # Delete only the first volume
        SystemVolumeManager.delete_volume(volume_path1)

        # Check that only the first volume is deleted
        assert not volume_path1.exists()
        assert volume_path2.exists()
