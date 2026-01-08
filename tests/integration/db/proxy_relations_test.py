"""Integration tests for proxy relations between models."""

import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import TemplateType
from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.shared.git_source import GitSource
from svs_core.users.user import User


class TestProxyRelations:
    """Tests for proxy relations between models."""

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_user_proxy_services(
        self,
        mocker: MockerFixture,
        mock_docker_network_create: object,
        mock_system_user_create: object,
    ) -> None:
        """Test UserModel.proxy_services returns related services."""
        # Create a user
        user = User.create(name="testuser", password="testpass123")

        # Initially, user should have no services
        assert user.proxy_services.count() == 0

        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a template
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="test-template",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Test template",
        )

        # Create a service for this user
        service = Service.create(
            name="test-service",
            template_id=template.id,
            user=user,
            image="nginx:latest",
        )

        # Verify proxy_services returns the service
        assert user.proxy_services.count() == 1
        assert user.proxy_services.first().id == service.id
        assert user.proxy_services.first().name == "test-service"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_template_proxy_services(
        self,
        mocker: MockerFixture,
        mock_docker_network_create: object,
        mock_system_user_create: object,
    ) -> None:
        """Test TemplateModel.proxy_services returns related services."""
        # Create a template
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="test-template",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Test template",
        )

        # Initially, template should have no services
        assert template.proxy_services.count() == 0

        # Create a user
        user = User.create(name="testuser", password="testpass123")

        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service using this template
        service = Service.create(
            name="test-service",
            template_id=template.id,
            user=user,
            image="nginx:latest",
        )

        # Verify proxy_services returns the service
        assert template.proxy_services.count() == 1
        assert template.proxy_services.first().id == service.id
        assert template.proxy_services.first().name == "test-service"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_proxy_template(
        self,
        mocker: MockerFixture,
        mock_docker_network_create: object,
        mock_system_user_create: object,
    ) -> None:
        """Test ServiceModel.proxy_template returns related template."""
        # Create a template
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="test-template",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Test template",
        )

        # Create a user
        user = User.create(name="testuser", password="testpass123")

        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service
        service = Service.create(
            name="test-service",
            template_id=template.id,
            user=user,
            image="nginx:latest",
        )

        # Verify proxy_template returns the template
        assert service.proxy_template.count() == 1
        assert service.proxy_template.first().id == template.id
        assert service.proxy_template.first().name == "test-template"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_proxy_user(
        self,
        mocker: MockerFixture,
        mock_docker_network_create: object,
        mock_system_user_create: object,
    ) -> None:
        """Test ServiceModel.proxy_user returns related user."""
        # Create a user
        user = User.create(name="testuser", password="testpass123")

        # Create a template
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="test-template",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Test template",
        )

        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service
        service = Service.create(
            name="test-service",
            template_id=template.id,
            user=user,
            image="nginx:latest",
        )

        # Verify proxy_user returns the user
        assert service.proxy_user.count() == 1
        assert service.proxy_user.first().id == user.id
        assert service.proxy_user.first().name == "testuser"

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
