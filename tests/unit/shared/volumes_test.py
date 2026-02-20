from pathlib import Path
from typing import Any

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
    # Create a mock that allows mkdir to run but mocks sudo commands
    original_run_command = __import__(
        "svs_core.shared.shell", fromlist=["run_command"]
    ).run_command

    def side_effect(command, **kwargs):
        # Let mkdir commands run normally
        if "mkdir" in command:
            import subprocess

            # Remove sudo prefix if present to avoid permission issues in test
            cmd_to_run = (
                command.replace("sudo -u svs ", "")
                .replace("sudo -u testuser ", "")
                .replace("sudo -u user1 ", "")
                .replace("sudo -u user2 ", "")
                .replace("sudo -u otheruser ", "")
            )
            subprocess.run(cmd_to_run, shell=True, check=False)
            return mocker.Mock(returncode=0, stdout="", stderr="")
        # Let rm commands run normally
        elif "rm -rf" in command:
            import subprocess

            # Remove sudo prefix if present to avoid permission issues in test
            cmd_to_run = (
                command.replace("sudo -u svs ", "")
                .replace("sudo -u testuser ", "")
                .replace("sudo -u user1 ", "")
                .replace("sudo -u user2 ", "")
                .replace("sudo -u otheruser ", "")
            )
            subprocess.run(cmd_to_run, shell=True, check=False)
            return mocker.Mock(returncode=0, stdout="", stderr="")
        # Mock sudo chown and chmod commands
        elif "sudo chown" in command or "sudo chmod" in command:
            return mocker.Mock(returncode=0, stdout="", stderr="")
        # For other commands, use the original
        return original_run_command(command, **kwargs)

    # Patch both locations: shell module (for create_directory/remove_directory internals)
    # and volumes module (for the direct run_command import in volumes.py)
    mocker.patch("svs_core.shared.shell.run_command", side_effect=side_effect)
    return mocker.patch("svs_core.shared.volumes.run_command", side_effect=side_effect)


@pytest.fixture
def mock_user(mocker):
    user = mocker.Mock()
    user.id = 123
    user.name = "testuser"
    return user


class TestVolumes:
    @pytest.mark.unit
    def test_generate_free_volume_creates_directory(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.exists()
        assert volume_path.is_dir()
        assert str(mock_user.id) in volume_path.parts
        assert len(volume_path.name) == 16

    @pytest.mark.unit
    def test_generate_free_volume_returns_absolute_path(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that generate_free_volume returns an absolute path."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.is_absolute()

    @pytest.mark.unit
    def test_generate_free_volume_generates_unique_paths(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that generate_free_volume generates unique paths for multiple
        calls."""
        volume_path1 = SystemVolumeManager.generate_free_volume(mock_user)
        volume_path2 = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path1 != volume_path2
        assert volume_path1.exists()
        assert volume_path2.exists()

    @pytest.mark.unit
    def test_generate_free_volume_creates_nested_directories(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
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
        self, mock_user: Any, tmp_path: Any, mock_run_command: Any
    ) -> None:
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
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
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
    def test_delete_user_volumes_with_nonexistent_user(self) -> None:
        # Should not raise an error
        SystemVolumeManager.delete_user_volumes(999)

    @pytest.mark.unit
    def test_delete_user_volumes_removes_only_user_volumes(
        self, mock_user: Any, mocker: Any, mock_run_command: Any
    ) -> None:
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
    def test_volume_id_has_correct_length(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)
        volume_id = volume_path.name

        assert len(volume_id) == 16
        assert volume_id.isalpha()
        assert volume_id.islower()

    @pytest.mark.unit
    def test_generate_free_volume_with_different_users(
        self, mocker: Any, mock_run_command: Any
    ) -> None:
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
    def test_delete_volume_removes_specific_volume(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        volume_path1 = SystemVolumeManager.generate_free_volume(mock_user)
        volume_path2 = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path1.exists()
        assert volume_path2.exists()

        # Delete only the first volume
        SystemVolumeManager.delete_volume(volume_path1)

        assert not volume_path1.exists()
        assert volume_path2.exists()

    @pytest.mark.unit
    def test_delete_volume_with_files(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
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
    def test_delete_volume_with_nonexistent_volume(self) -> None:
        nonexistent_path = SystemVolumeManager.BASE_PATH / "999" / "nonexistent"

        # Should not raise an error
        SystemVolumeManager.delete_volume(nonexistent_path)

    @pytest.mark.unit
    def test_delete_volume_with_custom_user(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test delete_volume with a custom user argument."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.exists()

        # Delete the volume with a custom user
        SystemVolumeManager.delete_volume(volume_path, user="testuser")

        assert not volume_path.exists()
        # Verify that remove_directory was called with the correct user
        mock_run_command.assert_called()

    @pytest.mark.unit
    def test_delete_volume_with_default_user(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test delete_volume uses default user 'svs' when not specified."""
        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert volume_path.exists()

        # Delete the volume without specifying user (should use default "svs")
        SystemVolumeManager.delete_volume(volume_path)

        assert not volume_path.exists()
        # Verify that remove_directory was called (with default user)
        mock_run_command.assert_called()

    @pytest.mark.unit
    def test_delete_volume_does_not_affect_other_volumes(
        self, mock_user: Any, mocker: Any, mock_run_command: Any
    ) -> None:
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

    @pytest.mark.unit
    def test_find_host_path_with_matching_volume(self) -> None:
        """Test finding host path when container path matches a volume
        mount."""
        from svs_core.docker.json_properties import Volume

        # Example from docstring:
        # container path: /usr/share/nginx/html/index.html
        # should map to host path: /var/svs/volumes/.../index.html
        host_path = "/var/svs/volumes/user123/volume1"
        volumes = [
            Volume(host_path=host_path, container_path="/usr/share/nginx/html"),
            Volume(host_path=None, container_path="/etc/nginx/conf.d"),
        ]

        container_path = Path("/usr/share/nginx/html/index.html")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        assert result is not None
        assert result == Path(host_path) / "index.html"

    @pytest.mark.unit
    def test_find_host_path_with_nested_container_path(self) -> None:
        """Test finding host path with deeply nested container paths."""
        from svs_core.docker.json_properties import Volume

        host_path = "/var/svs/volumes/user123/volume1"
        volumes = [
            Volume(host_path=host_path, container_path="/usr/share/nginx/html"),
        ]

        container_path = Path("/usr/share/nginx/html/subdir/deep/file.txt")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        assert result is not None
        assert result == Path(host_path) / "subdir" / "deep" / "file.txt"

    @pytest.mark.unit
    def test_find_host_path_with_no_matching_volume(self) -> None:
        """Test finding host path when no volume matches the container path."""
        from svs_core.docker.json_properties import Volume

        volumes = [
            Volume(
                host_path="/var/svs/volumes/user123/volume1",
                container_path="/usr/share/nginx/html",
            ),
            Volume(host_path=None, container_path="/etc/nginx/conf.d"),
        ]

        container_path = Path("/opt/app/data/file.txt")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        assert result is None

    @pytest.mark.unit
    def test_find_host_path_with_null_host_path(self) -> None:
        """Test finding host path when volume has null host path
        (anonymous)."""
        from svs_core.docker.json_properties import Volume

        volumes = [
            Volume(host_path=None, container_path="/etc/nginx/conf.d"),
        ]

        container_path = Path("/etc/nginx/conf.d/default.conf")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        # Should return None because host path is None
        assert result is None

    @pytest.mark.unit
    def test_find_host_path_with_multiple_volumes(self) -> None:
        """Test finding host path when multiple volumes are available."""
        from svs_core.docker.json_properties import Volume

        volumes = [
            Volume(
                host_path="/var/svs/volumes/user123/vol1",
                container_path="/usr/share/nginx/html",
            ),
            Volume(
                host_path="/var/svs/volumes/user123/vol2",
                container_path="/var/www/data",
            ),
            Volume(host_path=None, container_path="/etc/config"),
        ]

        # Test matching first volume
        result1 = SystemVolumeManager.find_host_path(
            Path("/usr/share/nginx/html/index.html"), volumes
        )
        assert result1 == Path("/var/svs/volumes/user123/vol1") / "index.html"

        # Test matching second volume
        result2 = SystemVolumeManager.find_host_path(
            Path("/var/www/data/file.dat"), volumes
        )
        assert result2 == Path("/var/svs/volumes/user123/vol2") / "file.dat"

        # Test no match
        result3 = SystemVolumeManager.find_host_path(
            Path("/opt/other/file.txt"), volumes
        )
        assert result3 is None

    @pytest.mark.unit
    def test_find_host_path_with_exact_volume_root(self) -> None:
        """Test finding host path when container path is exactly the volume
        root."""
        from svs_core.docker.json_properties import Volume

        host_path = "/var/svs/volumes/user123/volume1"
        volumes = [
            Volume(host_path=host_path, container_path="/usr/share/nginx/html"),
        ]

        # Container path is exactly the volume mount point
        container_path = Path("/usr/share/nginx/html")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        assert result is not None
        assert result == Path(host_path)

    @pytest.mark.unit
    def test_find_host_path_with_empty_volumes_list(self) -> None:
        """Test finding host path when volumes list is empty."""
        from svs_core.docker.json_properties import Volume

        volumes: list[Volume] = []
        container_path = Path("/usr/share/nginx/html/index.html")
        result = SystemVolumeManager.find_host_path(container_path, volumes)

        assert result is None

    @pytest.mark.unit
    def test_create_user_volume_creates_directory(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that create_user_volume creates the user directory when it doesn't exist."""
        user_dir = SystemVolumeManager.BASE_PATH / str(mock_user.id)
        assert not user_dir.exists()

        SystemVolumeManager.create_user_volume(mock_user)

        assert user_dir.exists()
        assert user_dir.is_dir()

    @pytest.mark.unit
    def test_create_user_volume_skips_existing_directory(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that create_user_volume does not raise when directory already exists."""
        user_dir = SystemVolumeManager.BASE_PATH / str(mock_user.id)
        user_dir.mkdir(parents=True, exist_ok=True)
        assert user_dir.exists()

        # Should not raise
        SystemVolumeManager.create_user_volume(mock_user)

        assert user_dir.exists()

    @pytest.mark.unit
    def test_create_user_volume_calls_chown(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that create_user_volume calls chown on the created directory."""
        SystemVolumeManager.create_user_volume(mock_user)

        chown_calls = [
            call
            for call in mock_run_command.call_args_list
            if "chown" in str(call)
        ]
        assert len(chown_calls) > 0
        assert mock_user.name in str(chown_calls[0])

    @pytest.mark.unit
    def test_generate_free_volume_creates_user_dir_when_missing(
        self, mock_user: Any, mock_run_command: Any
    ) -> None:
        """Test that generate_free_volume creates the user directory when it
        doesn't exist yet (the bug fix scenario)."""
        user_dir = SystemVolumeManager.BASE_PATH / str(mock_user.id)
        assert not user_dir.exists()

        volume_path = SystemVolumeManager.generate_free_volume(mock_user)

        assert user_dir.exists()
        assert user_dir.is_dir()
        assert volume_path.exists()
        assert volume_path.parent == user_dir
