"""Integration tests for proxy relations between models."""

import pytest

from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.shared.git_source import GitSource
from svs_core.users.user import User


class TestProxyRelations:
    """Tests for proxy relations between models."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_user_proxy_services(self, test_user: User, test_service: Service) -> None:
        """Test UserModel.proxy_services returns related services."""
        # Verify proxy_services returns the service
        assert test_user.proxy_services.count() == 1
        assert test_user.proxy_services.first().id == test_service.id
        assert test_user.proxy_services.first().name == "test-service"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_template_proxy_services(
        self, test_template: Template, test_service: Service
    ) -> None:
        """Test TemplateModel.proxy_services returns related services."""
        # Verify proxy_services returns the service
        assert test_template.proxy_services.count() == 1
        assert test_template.proxy_services.first().id == test_service.id
        assert test_template.proxy_services.first().name == "test-service"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_proxy_template(
        self, test_service: Service, test_template: Template
    ) -> None:
        """Test ServiceModel.proxy_template returns related template."""
        # Verify proxy_template returns the template
        assert test_service.proxy_template.count() == 1
        assert test_service.proxy_template.first().id == test_template.id
        assert test_service.proxy_template.first().name == "test-nginx"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_proxy_user(self, test_service: Service, test_user: User) -> None:
        """Test ServiceModel.proxy_user returns related user."""
        # Verify proxy_user returns the user
        assert test_service.proxy_user.count() == 1
        assert test_service.proxy_user.first().id == test_user.id
        assert test_service.proxy_user.first().name == "testuser"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_proxy_git_sources(self, test_service: Service) -> None:
        """Test ServiceModel.proxy_git_sources returns related git sources."""
        from pathlib import Path
        from tempfile import TemporaryDirectory

        # Initially, service should have no git sources
        assert test_service.proxy_git_sources.count() == 0

        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "repo"

            # Create a git source
            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            # Verify proxy_git_sources returns the git source
            assert test_service.proxy_git_sources.count() == 1
            assert test_service.proxy_git_sources.first().id == git_source.id
            assert test_service.proxy_git_sources.first().branch == "main"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_git_source_proxy_service(self, test_service: Service) -> None:
        """Test GitSourceModel.proxy_service returns related service."""
        from pathlib import Path
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmpdir:
            destination_path = Path(tmpdir) / "repo"

            # Create a git source
            git_source = GitSource.create(
                service_id=test_service.id,
                repository_url="https://github.com/user/repo.git",
                destination_path=destination_path,
                branch="main",
            )

            # Verify proxy_service returns the service
            assert git_source.proxy_service.count() == 1
            assert git_source.proxy_service.first().id == test_service.id
            assert git_source.proxy_service.first().name == test_service.name
