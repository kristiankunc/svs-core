import json
import os

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from django.db import transaction

from svs_core.db.models import ServiceStatus, TemplateType
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.network import DockerNetworkManager
from svs_core.docker.service import Service
from svs_core.docker.template import Template
from svs_core.users.system import SystemUserManager
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
                default_env={"NGINX_PORT": "80", "NGINX_HOST": "localhost"},
                default_ports=[{"container": 80, "host": 8080}],
                default_volumes=[
                    {"container": "/usr/share/nginx/html", "host": "/tmp/nginx"}
                ],
                start_cmd="nginx -g 'daemon off;'",
                healthcheck={"test": ["CMD", "curl", "-f", "http://localhost"]},
                labels={"app": "nginx", "version": "1.0"},
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
            exposed_ports=[{"container": 80, "host": 8080}],
            env={"NGINX_PORT": "80", "ENV_VAR": "test_value"},
            volumes=[{"container": "/usr/share/nginx/html", "host": "/tmp/nginx"}],
            command="nginx -g 'daemon off;'",
            healthcheck={"test": ["CMD", "curl", "-f", "http://localhost"]},
            labels={"app": "nginx", "environment": "test"},
            args=["--no-cache"],
            networks=["test-network"],
        )

        # Verify basic properties
        assert service.id is not None
        assert service.name == "test-service"
        assert service.domain == "test.example.com"
        assert service.image == "nginx:latest"
        assert service.container_id == "test_container_id"
        assert service.status == "created"

        # Verify Docker container creation was called with correct parameters
        mock_create_container.assert_called_once()
        call_args = mock_create_container.call_args[1]
        assert call_args["name"] == "test-service"
        assert call_args["image"] == "nginx:latest"
        assert call_args["command"] == "nginx -g 'daemon off;'"
        assert call_args["args"] == ["--no-cache"]
        assert call_args["ports"] == {80: 8080}

        # Verify JSON properties
        assert len(service.env_variables) == 2
        env_vars = {ev.key: ev.value for ev in service.env_variables}
        assert env_vars["NGINX_PORT"] == "80"
        assert env_vars["ENV_VAR"] == "test_value"

        assert len(service.port_mappings) == 1
        assert service.port_mappings[0].container_port == 80
        assert service.port_mappings[0].host_port == 8080

        assert len(service.volume_mappings) == 1
        assert service.volume_mappings[0].container_path == "/usr/share/nginx/html"
        assert service.volume_mappings[0].host_path == "/tmp/nginx"

        # Verify label handling
        assert "app" in {label.key for label in service.label_list}
        assert "environment" in {label.key for label in service.label_list}
        # Note: system labels like service_id and caddy aren't in service.label_list because
        # they're added during DockerContainerManager.create_container which is mocked

        # Verify healthcheck
        assert service.healthcheck_config is not None
        assert service.healthcheck_config.test == [
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
            override_env={"OVERRIDE_VAR": "override_value"},
            override_ports=[{"container": 443, "host": 8443}],
            override_volumes=[{"container": "/config", "host": "/tmp/config"}],
            override_command="nginx -g 'daemon off;' -c /config/nginx.conf",
            override_labels={"environment": "prod"},
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
        env_dict = {env.key: env.value for env in service.env_variables}
        assert env_dict["NGINX_PORT"] == "80"  # From template
        assert env_dict["NGINX_HOST"] == "localhost"  # From template
        assert env_dict["OVERRIDE_VAR"] == "override_value"  # From override

        # Verify ports (template + override)
        ports = [
            (port.container_port, port.host_port) for port in service.port_mappings
        ]
        assert (80, 8080) in ports  # From template
        assert (443, 8443) in ports  # From override

        # Verify volumes (template + override)
        volumes = [
            (vol.container_path, vol.host_path) for vol in service.volume_mappings
        ]
        assert ("/usr/share/nginx/html", "/tmp/nginx") in volumes  # From template
        assert ("/config", "/tmp/config") in volumes  # From override

        # Verify labels (template + override)
        labels = {label.key: label.value for label in service.label_list}
        assert labels["app"] == "nginx"  # From template
        assert labels["environment"] == "prod"  # From override
        assert labels["svs_user"] == test_user.name  # Automatically added
        # Note: system labels like service_id and caddy aren't in service.label_list because
        # they're added during DockerContainerManager.create_container which is mocked

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    @patch("svs_core.docker.service.DockerContainerManager.get_container")
    def test_service_lifecycle(
        self, mock_get_container, mock_create_container, test_template, test_user
    ):
        """Test service lifecycle (create, start, stop)."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "lifecycle_container_id"
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
        assert service.status == "created"

        # Start the service
        service.start()

        # Verify container.start() was called
        mock_container.start.assert_called_once()
        assert service.status == ServiceStatus.RUNNING

        # Stop the service
        service.stop()

        # Verify container.stop() was called
        mock_container.stop.assert_called_once()
        assert service.status == ServiceStatus.STOPPED

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    def test_service_property_conversions(
        self, mock_create_container, test_template, test_user
    ):
        """Test service property conversion methods."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "test_property_container"
        mock_create_container.return_value = mock_container

        # Create a service with various properties
        service = Service.create(
            name="property-service",
            template_id=test_template.id,
            user=test_user,
            env={"KEY1": "value1", "KEY2": "value2"},
            exposed_ports=[
                {"container": 80, "host": 8080},
                {"container": 443, "host": 8443},
            ],
            volumes=[
                {"container": "/data", "host": "/tmp/data"},
                {"container": "/config", "host": "/tmp/config"},
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost"],
                "interval": 30,
                "timeout": 10,
                "retries": 3,
                "start_period": 5,
            },
            labels={"app": "web", "version": "1.0"},
        )

        # Test to_env_dict
        env_dict = service.to_env_dict()
        assert env_dict == {"KEY1": "value1", "KEY2": "value2"}

        # Test to_ports_list
        ports_list = service.to_ports_list()
        assert len(ports_list) == 2
        assert {"container": 80, "host": 8080} in ports_list
        assert {"container": 443, "host": 8443} in ports_list

        # Test to_volumes_list
        volumes_list = service.to_volumes_list()
        assert len(volumes_list) == 2
        assert {"container": "/data", "host": "/tmp/data"} in volumes_list
        assert {"container": "/config", "host": "/tmp/config"} in volumes_list

        # Test to_labels_dict
        labels_dict = service.to_labels_dict()
        assert labels_dict["app"] == "web"
        assert labels_dict["version"] == "1.0"

        # Test to_healthcheck_dict
        healthcheck_dict = service.to_healthcheck_dict()
        assert healthcheck_dict is not None
        assert healthcheck_dict["test"] == ["CMD", "curl", "-f", "http://localhost"]
        assert healthcheck_dict["interval"] == 30
        assert healthcheck_dict["timeout"] == 10
        assert healthcheck_dict["retries"] == 3
        assert healthcheck_dict["start_period"] == 5

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    def test_service_string_representation(
        self, mock_create_container, test_template, test_user
    ):
        """Test the string representation of a service."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "test_string_container"
        mock_create_container.return_value = mock_container

        # Create a service
        service = Service.create(
            name="string-service",
            template_id=test_template.id,
            user=test_user,
            domain="string.example.com",
            env={"ENV_VAR": "test_value"},
            exposed_ports=[{"container": 80, "host": 8080}],
            volumes=[{"container": "/data", "host": "/tmp/data"}],
            healthcheck={"test": ["CMD", "echo", "healthcheck"]},
        )

        # Get string representation
        string_repr = str(service)

        # Verify key elements are present in string representation
        assert "string-service" in string_repr
        assert "string.example.com" in string_repr
        assert "test_string_container" in string_repr
        assert "ENV_VAR=test_value" in string_repr
        assert "80:8080" in string_repr
        assert "/data:/tmp/data" in string_repr
        assert "test='CMD echo healthcheck'" in string_repr

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.service.DockerContainerManager.create_container")
    def test_service_validation(self, mock_create_container, test_template, test_user):
        """Test validation during service creation."""
        # Mock container creation
        mock_container = MagicMock()
        mock_container.id = "test_validation_container"
        mock_create_container.return_value = mock_container

        # Test validation for empty name
        with pytest.raises(ValueError, match="Service name cannot be empty"):
            Service.create(
                name="",  # Empty name should raise ValueError
                template_id=test_template.id,
                user=test_user,
            )

        # Test validation for non-existent template
        with pytest.raises(ValueError, match="Template with ID .* does not exist"):
            Service.create(
                name="invalid-template-service",
                template_id=999999,  # Non-existent template ID
                user=test_user,
            )

        # Test validation for invalid port specification
        with pytest.raises(ValueError, match="Invalid port specification"):
            Service.create(
                name="invalid-port-service",
                template_id=test_template.id,
                user=test_user,
                exposed_ports=[{"invalid": "port"}],  # Missing 'container' key
            )

        # Test validation for invalid port type
        with pytest.raises(ValueError, match="Container port must be an integer"):
            Service.create(
                name="invalid-port-type-service",
                template_id=test_template.id,
                user=test_user,
                exposed_ports=[{"container": "not-an-integer", "host": 8080}],
            )

        # Test validation for invalid volume specification
        with pytest.raises(ValueError, match="Invalid volume specification"):
            Service.create(
                name="invalid-volume-service",
                template_id=test_template.id,
                user=test_user,
                volumes=[{"invalid": "volume"}],  # Missing 'container' key
            )

        # Test validation for invalid healthcheck
        with pytest.raises(ValueError, match="Healthcheck must contain a 'test' field"):
            Service.create(
                name="invalid-healthcheck-service",
                template_id=test_template.id,
                user=test_user,
                healthcheck={},  # Missing 'test' field
            )
