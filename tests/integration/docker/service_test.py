from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import ServiceStatus, TemplateType
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.users.user import User


@pytest.fixture
def test_template() -> Generator[Template, None, None]:
    """Create a test template for service creation tests."""
    with patch("svs_core.docker.template.DockerImageManager.exists", return_value=True):
        with patch("svs_core.docker.template.DockerImageManager.pull"):
            template = Template.create(
                name="test-nginx",
                type=TemplateType.IMAGE,
                image="nginx:alpine",
                description="Test Nginx Image",
                default_env=[
                    EnvVariable(key="NGINX_PORT", value="80"),
                    EnvVariable(key="NGINX_HOST", value="localhost"),
                ],
                default_ports=[ExposedPort(host_port=None, container_port=80)],
                default_volumes=[
                    Volume(
                        host_path="/tmp/nginx", container_path="/usr/share/nginx/html"
                    )
                ],
                start_cmd="nginx -g 'daemon off;'",
                healthcheck=Healthcheck(
                    test=["CMD", "curl", "-f", "http://localhost"],
                ),
                labels=[
                    Label(key="app", value="nginx"),
                    Label(key="version", value="1.0"),
                ],
                args=["--no-cache"],
            )
            yield template


@pytest.fixture
def test_user() -> Generator[User, None, None]:
    """Create a test user for service creation tests."""
    with patch("svs_core.users.user.DockerNetworkManager.create_network"):
        with patch("svs_core.users.user.SystemUserManager.create_user"):
            user = User.create(name="testuser", password="password123")
            yield user


class TestService:
    """Integration tests for the Service class."""

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    def test_service_create(self, mock_create_container, test_template, test_user):
        """Test creating a service directly."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "test_container_id"
        mock_create_container.return_value = mock_container

        # Create a service
        service = Service.create(
            name="test-service",
            template_id=test_template.id,
            user=test_user,
            domain="test.example.com",
            image="nginx:latest",
            exposed_ports=[ExposedPort(host_port=8080, container_port=80)],
            env=[
                EnvVariable(key="ENV_VAR", value="test_value"),
                EnvVariable(key="NGINX_PORT", value="80"),
            ],
            volumes=[
                Volume(host_path="/tmp/nginx", container_path="/usr/share/nginx/html")
            ],
            command="nginx -g 'daemon off;'",
            healthcheck=Healthcheck(
                test=["CMD", "curl", "-f", "http://localhost"],
            ),
            labels=[Label(key="environment", value="testing")],
            args=["--no-cache"],
            networks=["test-network"],
        )

        # Verify basic properties
        assert service.id is not None
        assert service.name == "test-service"
        assert service.domain == "test.example.com"
        assert service.image == "nginx:latest"
        assert service.container_id == "test_container_id"
        assert service.status == ServiceStatus.CREATED

        # Verify Docker container creation was called with correct parameters
        mock_create_container.assert_called_once()
        call_args = mock_create_container.call_args[1]
        assert call_args["name"] == "test-service"
        assert call_args["image"] == "nginx:latest"
        assert call_args["command"] == "nginx -g 'daemon off;'"
        assert call_args["args"] == ["--no-cache"]
        assert call_args["ports"] == {80: 8080}

        # Verify JSON properties
        assert len(service.env) == 2
        assert service.env[0].key == "ENV_VAR"
        assert service.env[0].value == "test_value"
        assert service.env[1].key == "NGINX_PORT"
        assert service.env[1].value == "80"

        assert len(service.exposed_ports) == 1
        assert service.exposed_ports[0].container_port == 80
        assert service.exposed_ports[0].host_port == 8080

        assert len(service.volumes) == 1
        assert service.volumes[0].container_path == "/usr/share/nginx/html"
        assert service.volumes[0].host_path == "/tmp/nginx"

        # Verify label handling
        assert len(service.labels) >= 1
        label_dict = {label.key: label.value for label in service.labels}
        assert label_dict["environment"] == "testing"

        # Verify healthcheck
        assert service.healthcheck is not None
        assert service.healthcheck.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost",
        ]

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    @patch("svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000)
    @patch("svs_core.shared.volumes.SystemVolumeManager.generate_free_volume")
    def test_service_create_from_template(
        self,
        mock_generate_volume,
        mock_find_free_port,
        mock_create_container,
        test_template,
        test_user,
    ):
        """Test creating a service from a template."""

        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "test_container_from_template"
        mock_create_container.return_value = mock_container

        # Mock volume generation
        mock_volume_path = MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume.return_value = mock_volume_path

        # Create service from template
        service = Service.create_from_template(
            name="template-service",
            template_id=test_template.id,
            user=test_user,
            domain="template.example.com",
            override_env=[EnvVariable(key="OVERRIDE_VAR", value="override_value")],
            override_ports=[ExposedPort(host_port=8443, container_port=443)],
            override_volumes=[
                Volume(host_path="/tmp/config", container_path="/config")
            ],
            override_command="nginx -g 'daemon off;' -c /config/nginx.conf",
            override_labels=[Label(key="environment", value="prod")],
        )

        # Verify basic properties
        assert service.id is not None
        assert service.name == "template-service"
        assert service.domain == "template.example.com"
        assert service.image == test_template.image
        assert service.container_id == "test_container_from_template"

        # Verify command was overridden
        assert service.command == "nginx -g 'daemon off;' -c /config/nginx.conf"

        # Verify environment variables (template + override)
        env_dict = {env.key: env.value for env in service.env}
        assert env_dict["OVERRIDE_VAR"] == "override_value"  # From override

        # Verify ports (template + override)
        ports = [
            (port.container_port, port.host_port) for port in service.exposed_ports
        ]
        assert (443, 8443) in ports  # From override

        # Verify volumes (template + override)
        volumes = [(vol.container_path, vol.host_path) for vol in service.volumes]
        assert ("/config", "/tmp/config") in volumes  # From override

        # Verify labels (template + override)
        labels = {label.key: label.value for label in service.labels}
        assert labels["environment"] == "prod"  # From override
        assert labels["svs_user"] == test_user.name  # Automatically added

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    @patch("svs_core.docker.service.DockerContainerManager.get_container")
    def test_service_lifecycle(
        self,
        mock_get_container: MagicMock,
        mock_create_container: MagicMock,
        test_template: Template,
        test_user: User,
        mocker: MockerFixture,
    ) -> None:
        """Test service lifecycle (create, start, stop)."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "lifecycle_container_id"
        mock_container.status = "created"  # Initial status
        mock_create_container.return_value = mock_container
        mock_get_container.return_value = mock_container

        # Create the service
        service = Service.create(
            name="lifecycle-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        assert service.container_id == "lifecycle_container_id"
        assert service.status == ServiceStatus.CREATED

        # Start the service and update mock status
        mocker.patch.object(
            mock_container,
            "start",
            side_effect=lambda: setattr(mock_container, "status", "running"),
        )
        service.start()

        # Verify container.start() was called
        mock_container.start.assert_called_once()
        assert service.status == ServiceStatus.RUNNING  # type: ignore

        # Stop the service and update mock status
        mocker.patch.object(
            mock_container,
            "stop",
            side_effect=lambda: setattr(mock_container, "status", "stopped"),
        )
        service.stop()

        # Verify container.stop() was called
        mock_container.stop.assert_called_once()
        assert service.status == ServiceStatus.STOPPED
