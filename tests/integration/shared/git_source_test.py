"""Integration tests for GitSource model and operations."""

from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from svs_core.docker.service import Service
from svs_core.shared.git_source import GitSource


class TestGitSourceIntegration:
    """Integration tests for GitSource creation and validation."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_git_source_success(self, test_service: Service) -> None:
        """Test successful GitSource creation."""
        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "repo"

            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            assert git_source.id is not None
            assert git_source.service_id == test_service.id
            assert git_source.branch == "main"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_git_source_invalid_service_id(self) -> None:
        """Test GitSource creation fails with invalid service ID."""
        with TemporaryDirectory() as tmpdir:
            with pytest.raises(Service.DoesNotExist):
                GitSource.create(
                    service_id=99999,
                    repository_url="https://github.com/user/repo.git",
                    destination_path=Path(tmpdir) / "repo",
                    branch="main",
                )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_git_source_relative_path(self, test_service: Service) -> None:
        """Test GitSource creation fails with relative path."""
        with pytest.raises(
            ValueError, match="destination_path must be an absolute path"
        ):
            GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=Path("relative/path"),
                branch="main",
            )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_git_source_invalid_url(self, test_service: Service) -> None:
        """Test GitSource creation fails with invalid URL."""
        with TemporaryDirectory() as tmpdir:
            with pytest.raises(ValueError, match="repository_url must be a valid URL"):
                GitSource.create(
                    service_id=test_service.id,
                    repository_url="invalid-url",
                    destination_path=Path(tmpdir) / "repo",
                    branch="main",
                )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_git_source_invalid_branch(self, test_service: Service) -> None:
        """Test GitSource creation fails with invalid branch."""
        with TemporaryDirectory() as tmpdir:
            with pytest.raises(
                ValueError, match="branch cannot be an empty string or contain spaces"
            ):
                GitSource.create(
                    service_id=test_service.id,
                    repository_url="https://github.com/user/repo.git",
                    destination_path=Path(tmpdir) / "repo",
                    branch="invalid branch",
                )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_is_cloned(self, test_service: Service) -> None:
        """Test is_cloned detection."""
        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "repo"
            destination_path.mkdir(parents=True)
            (destination_path / ".git").mkdir(parents=True)

            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            assert git_source.is_cloned()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_download_creates_parent_directory(self, test_service: Service) -> None:
        """Test download creates parent directory if it doesn't exist."""
        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "nonexistent" / "repo"

            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            with patch("svs_core.shared.git_source.create_directory") as mock_mkdir:
                with patch("svs_core.shared.git_source.run_command") as mock_run:
                    mock_run.return_value = MagicMock(stdout="")
                    git_source.download()

                    # Verify create_directory was called for parent
                    mock_mkdir.assert_called_once()
                    assert str(destination_path.parent) in mock_mkdir.call_args[0][0]

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_download_cleans_existing_directory(self, test_service: Service) -> None:
        """Test download removes existing destination before cloning."""
        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "repo"
            destination_path.mkdir(parents=True)

            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            with patch("svs_core.shared.git_source.run_command") as mock_run:
                mock_run.return_value = MagicMock(stdout="")
                git_source.download()

                # Verify rm -rf was called before clone
                call_strings = [call[0][0] for call in mock_run.call_args_list]
                assert any("rm -rf" in cmd for cmd in call_strings)
                assert any("git clone" in cmd for cmd in call_strings)
