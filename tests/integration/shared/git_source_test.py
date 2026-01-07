"""Integration tests for GitSource model and operations."""

from pathlib import Path
from tempfile import TemporaryDirectory

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
