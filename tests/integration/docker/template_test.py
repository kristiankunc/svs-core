import json
import os

from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio

from asgiref.sync import sync_to_async
from django.db import transaction

from svs_core.db.models import TemplateType
from svs_core.docker.image import DockerImageManager
from svs_core.docker.template import Template


class TestTemplate:

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=False)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_create_image_template(self, mock_pull, mock_exists):
        """Test creating an image-based template."""
        # Use a small, public image for testing
        image_name = "alpine"
        tag = "latest"

        # Create a template using the factory method
        template = Template.create(
            name="test-alpine",
            type=TemplateType.IMAGE,
            image=f"{image_name}:{tag}",
            description="Test Alpine Image",
            default_env={"TEST_VAR": "test_value"},
            default_ports=[{"container": 80, "host": 8080}],
            default_volumes=[{"container": "/data", "host": "/tmp/data"}],
            start_cmd="sh -c 'echo hello'",
            labels={"app": "test"},
            args=["ARG1=value1"],
        )

        # Verify basic properties
        assert template.id is not None
        assert template.name == "test-alpine"
        assert template.type == TemplateType.IMAGE
        assert template.image == "alpine:latest"
        assert template.description == "Test Alpine Image"
        assert template.start_cmd == "sh -c 'echo hello'"

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_once_with(image_name, tag)

        # Verify JSON properties
        assert len(template.env_variables) == 1
        assert template.env_variables[0].key == "TEST_VAR"
        assert template.env_variables[0].value == "test_value"

        assert len(template.exposed_ports) == 1
        assert template.exposed_ports[0].container_port == 80
        assert template.exposed_ports[0].host_port == 8080

        assert len(template.volumes) == 1
        assert template.volumes[0].container_path == "/data"
        assert template.volumes[0].host_path == "/tmp/data"

        assert len(template.label_list) == 1
        assert template.label_list[0].key == "app"
        assert template.label_list[0].value == "test"

        assert len(template.arguments) == 1
        assert template.arguments[0] == "ARG1=value1"

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=True)
    @patch("svs_core.docker.template.DockerImageManager.build_from_dockerfile")
    def test_create_build_template(self, mock_build, mock_exists):
        """Test creating a build-based template."""
        dockerfile_content = """
        FROM alpine:latest
        RUN apk add --no-cache python3
        WORKDIR /app
        CMD ["python3", "--version"]
        """

        template = Template.create(
            name="test-build",
            type=TemplateType.BUILD,
            dockerfile=dockerfile_content,
            description="Test Build Template",
        )

        assert template.id is not None
        assert template.name == "test-build"
        assert template.type == TemplateType.BUILD
        assert template.dockerfile == dockerfile_content
        assert template.description == "Test Build Template"

        # Verify build_from_dockerfile was called correctly
        mock_build.assert_called_once_with("test-build", dockerfile_content)

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=True)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_template_properties(self, mock_pull, mock_exists):
        """Test template property accessors."""
        template = Template.create(
            name="test-properties",
            type=TemplateType.IMAGE,
            image="nginx:alpine",
            default_env={"KEY1": "value1", "KEY2": "value2"},
            default_ports=[
                {"container": 80, "host": 8080},
                {"container": 443, "host": 8443},
            ],
            default_volumes=[
                {"container": "/data", "host": "/tmp/data"},
                {"container": "/config", "host": None},
            ],
            healthcheck={
                "test": ["CMD", "curl", "-f", "http://localhost"],
                "interval": 3,
                "timeout": 5,
                "retries": 3,
                "start_period": 5,
            },
            labels={"app": "web", "environment": "test"},
        )

        # Test env_variables property
        assert len(template.env_variables) == 2
        env_vars = {ev.key: ev.value for ev in template.env_variables}
        assert env_vars == {"KEY1": "value1", "KEY2": "value2"}

        # Test exposed_ports property
        assert len(template.exposed_ports) == 2
        assert template.exposed_ports[0].container_port == 80
        assert template.exposed_ports[0].host_port == 8080
        assert template.exposed_ports[1].container_port == 443
        assert template.exposed_ports[1].host_port == 8443

        # Test volumes property
        assert len(template.volumes) == 2
        assert template.volumes[0].container_path == "/data"
        assert template.volumes[0].host_path == "/tmp/data"
        assert template.volumes[1].container_path == "/config"
        assert template.volumes[1].host_path is None

        # Test healthcheck_config property
        assert template.healthcheck_config is not None
        assert template.healthcheck_config.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost",
        ]

        assert int(template.healthcheck_config.interval or 0) == 3
        assert int(template.healthcheck_config.timeout or 0) == 5
        assert int(template.healthcheck_config.retries or 0) == 3
        assert int(template.healthcheck_config.start_period or 0) == 5

        # Test label_list property
        assert len(template.label_list) == 2
        labels = {label.key: label.value for label in template.label_list}
        assert labels == {"app": "web", "environment": "test"}

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=False)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_import_from_json(self, mock_pull, mock_exists):
        """Test importing a template from JSON data."""
        json_data = {
            "name": "json-template",
            "type": "image",
            "image": "redis:alpine",
            "description": "Redis template from JSON",
            "default_env": {"REDIS_PORT": "6379", "REDIS_PASSWORD": "secret"},
            "default_ports": [{"container": 6379, "host": 6379}],
            "default_volumes": [{"container": "/data", "host": "/var/redis/data"}],
            "start_cmd": "redis-server --requirepass secret",
            "labels": {"service": "cache", "version": "7.0"},
        }

        template = Template.import_from_json(json_data)

        assert template.id is not None
        assert template.name == "json-template"
        assert template.type == TemplateType.IMAGE
        assert template.image == "redis:alpine"
        assert template.description == "Redis template from JSON"

        # Verify the template properties
        assert len(template.env_variables) == 2
        env_vars = {ev.key: ev.value for ev in template.env_variables}
        assert env_vars == {"REDIS_PORT": "6379", "REDIS_PASSWORD": "secret"}

        assert len(template.exposed_ports) == 1
        assert template.exposed_ports[0].container_port == 6379
        assert template.exposed_ports[0].host_port == 6379

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_with("redis", "alpine")

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=True)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_template_string_representation(self, mock_pull, mock_exists):
        """Test the string representation of a template."""
        template = Template.create(
            name="string-test",
            type=TemplateType.IMAGE,
            image="busybox:latest",
            description="Test string representation",
            default_env={"TEST": "value"},
            default_ports=[{"container": 8080, "host": 80}],
            default_volumes=[{"container": "/app", "host": "/host/app"}],
            healthcheck={"test": ["CMD", "test", "-e", "/tmp/healthy"]},
        )

        string_repr = str(template)

        # Verify key elements are present in string representation
        assert "string-test" in string_repr
        assert "busybox:latest" in string_repr
        assert "TEST=value" in string_repr
        assert "8080:80" in string_repr
        assert "/app:/host/app" in string_repr
        assert "test='CMD test -e /tmp/healthy'" in string_repr

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=False)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_import_from_nginx_json_file(self, mock_pull, mock_exists):
        """Test importing a template from the nginx.json file."""
        # Path to the nginx.json template file
        template_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "service_templates",
            "nginx.json",
        )

        # Read the JSON template file
        with open(template_path, "r") as f:
            nginx_template = json.load(f)

        # Import the template from JSON
        template = Template.import_from_json(nginx_template)

        # Verify basic properties
        assert template.id is not None
        assert template.name == "nginx-webserver"
        assert template.type == TemplateType.IMAGE
        assert template.image == "nginx:latest"
        assert template.description == "A minimal NGINX web server with default config"
        assert template.start_cmd is None

        # Verify ports
        assert len(template.exposed_ports) == 1
        assert template.exposed_ports[0].container_port == 80
        assert template.exposed_ports[0].host_port is None

        # Verify volumes
        assert len(template.volumes) == 2
        container_paths = [vol.container_path for vol in template.volumes]
        assert "/usr/share/nginx/html" in container_paths
        assert "/etc/nginx/conf.d" in container_paths

        # Verify healthcheck
        assert template.healthcheck_config is not None
        assert template.healthcheck_config.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost/",
        ]
        assert template.healthcheck_config.retries == 3

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_with("nginx", "latest")

    @pytest.mark.integration
    @pytest.mark.django_db
    @patch("svs_core.docker.template.DockerImageManager.exists", return_value=True)
    @patch("svs_core.docker.template.DockerImageManager.pull")
    def test_validation_errors(self, mock_pull, mock_exists):
        """Test validation errors when creating templates."""
        # Test empty name
        with pytest.raises(ValueError, match="Template name cannot be empty"):
            Template.create(name="", type=TemplateType.IMAGE, image="alpine")

        # Test missing image for IMAGE type
        with pytest.raises(
            ValueError, match="Image type templates must specify an image"
        ):
            Template.create(name="test-missing-image", type=TemplateType.IMAGE)

        # Test missing dockerfile for BUILD type
        with pytest.raises(
            ValueError, match="Build type templates must specify a dockerfile"
        ):
            Template.create(name="test-missing-dockerfile", type=TemplateType.BUILD)

        # Test invalid port specification
        with pytest.raises(
            ValueError, match="Port specification must contain a 'container' field"
        ):
            Template.create(
                name="test-invalid-port",
                type=TemplateType.IMAGE,
                image="alpine",
                default_ports=[{"host": 8080}],  # Missing container field
            )

        # Test invalid healthcheck
        with pytest.raises(ValueError, match="Healthcheck must contain a 'test' field"):
            Template.create(
                name="test-invalid-healthcheck",
                type=TemplateType.IMAGE,
                image="alpine",
                healthcheck={"interval": 30000000000},  # Missing test field
            )
