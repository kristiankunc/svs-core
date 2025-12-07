import json
import os

import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import TemplateType
from svs_core.docker.json_properties import (
    DefaultContent,
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.template import Template


class TestTemplate:

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_image_template(self, mocker: MockerFixture) -> None:
        mock_exists = mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mock_pull = mocker.patch("svs_core.docker.template.DockerImageManager.pull")

        # Use a small, public image for testing
        image_name = "alpine"
        tag = "latest"

        # Create a template using the factory method
        template = Template.create(
            name="test-alpine",
            type=TemplateType.IMAGE,
            image=f"{image_name}:{tag}",
            description="Test Alpine Image",
            default_env=[EnvVariable(key="TEST_VAR", value="test_value")],
            default_ports=[ExposedPort(container_port=80, host_port=8080)],
            default_volumes=[Volume(container_path="/data", host_path="/tmp/data")],
            start_cmd="sh -c 'echo hello'",
            labels=[Label(key="app", value="test")],
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
        mock_pull.assert_called_once_with(f"{image_name}:{tag}")

        # Verify JSON properties
        assert len(template.default_env) == 1
        assert template.default_env[0].key == "TEST_VAR"
        assert template.default_env[0].value == "test_value"

        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 80
        assert template.default_ports[0].host_port == 8080

        assert len(template.default_volumes) == 1
        assert template.default_volumes[0].container_path == "/data"
        assert template.default_volumes[0].host_path == "/tmp/data"

        assert len(template.labels) == 1
        assert template.labels[0].key == "app"
        assert template.labels[0].value == "test"

        assert len(template.args) == 1
        assert template.args[0] == "ARG1=value1"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_template_with_default_contents(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")

        # Create a template with default contents
        template = Template.create(
            name="test-contents",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Test template with default contents",
            default_contents=[
                DefaultContent(
                    location="/etc/nginx/conf.d/default.conf",
                    content="server { listen 80; }",
                ),
                DefaultContent(
                    location="/usr/share/nginx/html/index.html",
                    content="<html><body>Hello</body></html>",
                ),
            ],
        )

        # Verify basic properties
        assert template.id is not None
        assert template.name == "test-contents"

        # Verify default_contents
        assert len(template.default_contents) == 2

        # Verify first content
        assert template.default_contents[0].location == "/etc/nginx/conf.d/default.conf"
        assert template.default_contents[0].content == "server { listen 80; }"

        # Verify second content
        assert (
            template.default_contents[1].location == "/usr/share/nginx/html/index.html"
        )
        assert template.default_contents[1].content == "<html><body>Hello</body></html>"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_build_template(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
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

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_template_properties(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="test-properties",
            type=TemplateType.IMAGE,
            image="nginx:alpine",
            default_env=[
                EnvVariable(key="KEY1", value="value1"),
                EnvVariable(key="KEY2", value="value2"),
            ],
            default_ports=[
                ExposedPort(container_port=80, host_port=8080),
                ExposedPort(container_port=443, host_port=8443),
            ],
            default_volumes=[
                Volume(container_path="/data", host_path="/tmp/data"),
                Volume(container_path="/config", host_path=None),
            ],
            healthcheck=Healthcheck(
                test=["CMD", "curl", "-f", "http://localhost"],
                interval=3,
                timeout=5,
                retries=3,
                start_period=5,
            ),
            labels=[
                Label(key="app", value="web"),
                Label(key="environment", value="test"),
            ],
        )

        # Test env_variables property
        assert len(template.default_env) == 2
        env_vars = {ev.key: ev.value for ev in template.default_env}
        assert env_vars == {"KEY1": "value1", "KEY2": "value2"}

        # Test exposed_ports property
        assert len(template.default_ports) == 2
        assert template.default_ports[0].container_port == 80
        assert template.default_ports[0].host_port == 8080
        assert template.default_ports[1].container_port == 443
        assert template.default_ports[1].host_port == 8443

        # Test volumes property
        assert len(template.default_volumes) == 2
        assert template.default_volumes[0].container_path == "/data"
        assert template.default_volumes[0].host_path == "/tmp/data"
        assert template.default_volumes[1].container_path == "/config"
        assert template.default_volumes[1].host_path is None

        # Test healthcheck_config property
        assert template.healthcheck is not None
        assert (
            template.healthcheck.test
            == Healthcheck(test=["CMD", "curl", "-f", "http://localhost"]).test
        )
        assert int(template.healthcheck.interval) == 3  # type: ignore
        assert int(template.healthcheck.timeout) == 5  # type: ignore
        assert int(template.healthcheck.retries) == 3  # type: ignore
        assert int(template.healthcheck.start_period) == 5  # type: ignore

        # Test label_list property
        assert len(template.labels) == 2
        labels = {label.key: label.value for label in template.labels}
        assert labels == {"app": "web", "environment": "test"}

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_json(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mock_pull = mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        json_data = {
            "name": "json-template",
            "type": "image",
            "image": "redis:alpine",
            "description": "Redis template from JSON",
            "default_env": [
                {"key": "REDIS_PORT", "value": "6379"},
                {"key": "REDIS_PASSWORD", "value": "secret"},
            ],
            "default_ports": [{"container": 6379, "host": 6379}],
            "default_volumes": [{"host": "/var/redis/data", "container": "/data"}],
            "start_cmd": "redis-server --requirepass secret",
            "labels": [
                {"key": "service", "value": "cache"},
                {"key": "version", "value": "7.0"},
            ],
        }

        template = Template.import_from_json(json_data)

        assert template.id is not None
        assert template.name == "json-template"
        assert template.type == TemplateType.IMAGE
        assert template.image == "redis:alpine"
        assert template.description == "Redis template from JSON"

        # Verify the template properties
        assert len(template.default_env) == 2
        env_vars = {ev.key: ev.value for ev in template.default_env}
        assert env_vars == {"REDIS_PORT": "6379", "REDIS_PASSWORD": "secret"}

        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 6379
        assert template.default_ports[0].host_port == 6379

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_with("redis:alpine")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_json_new_schema_format(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        json_data = {
            "name": "django-app",
            "type": "build",
            "description": "Django application",
            "dockerfile": "FROM python:3.11-slim\nWORKDIR /app",
            "default_env": [
                {"key": "DEBUG", "value": "True"},
                {"key": "DJANGO_SETTINGS_MODULE", "value": "project.settings"},
            ],
            "default_ports": [{"container": 8000, "host": None}],
            "default_volumes": [{"container": "/app/data", "host": None}],
            "default_contents": [
                {
                    "location": "/app/manage.py",
                    "content": "#!/usr/bin/env python\nimport os\nimport sys",
                },
                {
                    "location": "/app/requirements.txt",
                    "content": "Django==5.0\npsycopg2-binary==2.9",
                },
            ],
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:8000/"],
                "interval": 30,
                "timeout": 10,
                "retries": 3,
                "start_period": 5,
            },
            "start_cmd": "python manage.py runserver 0.0.0.0:8000",
            "args": [],
        }

        template = Template.import_from_json(json_data)

        assert template.id is not None
        assert template.name == "django-app"
        assert template.type == TemplateType.BUILD
        assert template.description == "Django application"
        assert template.dockerfile == "FROM python:3.11-slim\nWORKDIR /app"

        # Verify environment variables
        assert len(template.default_env) == 2
        env_vars = {ev.key: ev.value for ev in template.default_env}
        assert env_vars == {
            "DEBUG": "True",
            "DJANGO_SETTINGS_MODULE": "project.settings",
        }

        # Verify ports (new schema format: container=8000, host=None)
        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 8000
        assert template.default_ports[0].host_port is None

        # Verify volumes (new schema format: container=/app/data, host=None)
        assert len(template.default_volumes) == 1
        assert template.default_volumes[0].container_path == "/app/data"
        assert template.default_volumes[0].host_path is None

        # Verify default_contents
        assert len(template.default_contents) == 2
        content_dict = {
            content.location: content.content for content in template.default_contents
        }
        assert "/app/manage.py" in content_dict
        assert "/app/requirements.txt" in content_dict
        assert "import os" in content_dict["/app/manage.py"]
        assert "Django==5.0" in content_dict["/app/requirements.txt"]

        # Verify healthcheck
        assert template.healthcheck is not None
        assert template.healthcheck.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost:8000/",
        ]
        assert (
            template.healthcheck.interval is not None
            and int(template.healthcheck.interval) == 30
        )
        assert (
            template.healthcheck.timeout is not None
            and int(template.healthcheck.timeout) == 10
        )
        assert (
            template.healthcheck.retries is not None
            and int(template.healthcheck.retries) == 3
        )
        assert (
            template.healthcheck.start_period is not None
            and int(template.healthcheck.start_period) == 5
        )

        assert template.start_cmd == "python manage.py runserver 0.0.0.0:8000"
        assert template.args == []

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_json_new_schema_format_old(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        template = Template.create(
            name="string-test",
            type=TemplateType.IMAGE,
            image="busybox:latest",
            description="Test string representation",
            default_env=[EnvVariable(key="TEST", value="value")],
            default_ports=[ExposedPort(host_port=80, container_port=8080)],
            default_volumes=[Volume(container_path="/app", host_path="/host/app")],
            healthcheck=Healthcheck(test=["CMD", "test", "-e", "/tmp/healthy"]),
        )

        string_repr = str(template)
        print("\n\n")
        print(string_repr)

        # Verify key elements are present in string representation
        assert "string-test" in string_repr
        assert "busybox:latest" in string_repr
        assert "TEST=value" in string_repr
        assert "80=8080" in string_repr  # Now host_port=key, container_port=value
        assert "/app=/host/app" in string_repr
        assert "test=['CMD', 'test', '-e', '/tmp/healthy']" in string_repr

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_nginx_json_file(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mock_pull = mocker.patch("svs_core.docker.template.DockerImageManager.pull")
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
        assert template.image == "lscr.io/linuxserver/nginx:latest"
        assert template.description == "A minimal NGINX web server with default config"
        assert template.start_cmd is None

        # Verify ports
        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 80
        assert template.default_ports[0].host_port is None

        # Verify volumes
        assert len(template.default_volumes) == 1
        container_paths = [vol.container_path for vol in template.default_volumes]
        assert "/config" in container_paths

        # Verify default_contents
        assert len(template.default_contents) == 1
        content_locations = {
            content.location: content.content for content in template.default_contents
        }
        assert "/config/www/index.html" in content_locations
        assert "Welcome to NGINX!" in content_locations["/config/www/index.html"]

        # Verify healthcheck
        assert template.healthcheck is not None
        assert template.healthcheck.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost/",
        ]
        assert template.healthcheck.retries == 3

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_with("lscr.io/linuxserver/nginx:latest")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_mysql_json_file(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mock_pull = mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        # Path to the mysql.json template file
        template_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "service_templates",
            "mysql.json",
        )

        # Read the JSON template file
        with open(template_path, "r") as f:
            mysql_template = json.load(f)

        # Import the template from JSON
        template = Template.import_from_json(mysql_template)

        # Verify basic properties
        assert template.id is not None
        assert template.name == "mysql-database"
        assert template.type == TemplateType.IMAGE
        assert template.image == "mysql:latest"
        assert template.description == "MySQL database"
        assert template.start_cmd is None

        # Verify environment variables - should have 4 unique keys but 5 total entries
        # (MYSQL_PASSWORD appears twice)
        assert len(template.default_env) == 5
        env_vars = [ev.key for ev in template.default_env]
        assert "MYSQL_ROOT_PASSWORD" in env_vars
        assert "MYSQL_DATABASE" in env_vars
        assert "MYSQL_USER" in env_vars
        # Verify MYSQL_PASSWORD appears twice
        assert env_vars.count("MYSQL_PASSWORD") == 2

        # Verify ports
        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 3306
        assert template.default_ports[0].host_port is None

        # Verify volumes
        assert len(template.default_volumes) == 1
        assert template.default_volumes[0].container_path == "/var/lib/mysql"
        assert template.default_volumes[0].host_path is None

        # Verify healthcheck
        assert template.healthcheck is not None
        assert template.healthcheck.test == [
            "CMD",
            "mysqladmin",
            "ping",
        ]
        assert template.healthcheck.interval == 30
        assert template.healthcheck.timeout == 10
        assert template.healthcheck.retries == 5
        assert template.healthcheck.start_period == 20

        # Verify DockerImageManager.pull was called correctly
        mock_pull.assert_called_with("mysql:latest")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_import_from_django_json_file(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        # Path to the django.json template file
        template_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "service_templates",
            "django.json",
        )

        # Read the JSON template file
        with open(template_path, "r") as f:
            django_template = json.load(f)

        # Import the template from JSON
        template = Template.import_from_json(django_template)

        # Verify basic properties
        assert template.id is not None
        assert template.name == "django-app"
        assert template.type == TemplateType.BUILD
        assert template.dockerfile is not None
        assert "FROM python:3.11-slim" in template.dockerfile
        assert (
            template.description
            == "Django application container built on-demand from source"
        )
        assert template.start_cmd == "python manage.py runserver 0.0.0.0:8000"

        # Verify environment variables
        assert len(template.default_env) == 2
        env_vars = {ev.key: ev.value for ev in template.default_env}
        assert env_vars["DEBUG"] == "True"
        assert env_vars["DJANGO_SETTINGS_MODULE"] == "project.settings"

        # Verify ports
        assert len(template.default_ports) == 1
        assert template.default_ports[0].container_port == 8000
        assert template.default_ports[0].host_port is None

        # Verify volumes
        assert len(template.default_volumes) == 1
        assert template.default_volumes[0].container_path == "/app/data"
        assert template.default_volumes[0].host_path is None

        # Verify healthcheck
        assert template.healthcheck is not None
        assert template.healthcheck.test == [
            "CMD",
            "curl",
            "-f",
            "http://localhost:8000/",
        ]
        assert template.healthcheck.interval == 30
        assert template.healthcheck.timeout == 10
        assert template.healthcheck.retries == 3
        assert template.healthcheck.start_period == 5

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_validation_errors(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
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

        # Test invalid healthcheck
        with pytest.raises(ValueError, match="Healthcheck must contain a 'test' field"):
            Template.create(
                name="test-invalid-healthcheck",
                type=TemplateType.IMAGE,
                image="alpine",
                healthcheck=Healthcheck(test=[]),
            )

        # Test invalid default_contents - empty location
        with pytest.raises(
            ValueError, match="Default content location cannot be empty"
        ):
            Template.create(
                name="test-invalid-content",
                type=TemplateType.IMAGE,
                image="alpine",
                default_contents=[DefaultContent(location="", content="test")],
            )

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_template_without_services(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        mock_remove = mocker.patch("svs_core.docker.template.DockerImageManager.remove")
        """Test deleting a template that is not associated with any
        services."""
        mock_image_exists = mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )

        template = Template.create(
            name="test-delete",
            type=TemplateType.IMAGE,
            image="alpine:latest",
            description="Template to delete",
        )

        template_id = template.id

        # Verify template exists
        assert Template.objects.filter(id=template_id).exists()

        # Delete the template
        template.delete()

        # Verify template is deleted from database
        assert not Template.objects.filter(id=template_id).exists()

        # Verify DockerImageManager.remove was called with the correct image
        mock_remove.assert_called_once_with("alpine:latest")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_template_with_services_raises_error(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=False
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")
        mocker.patch("svs_core.users.user.DockerNetworkManager.create_network")
        mocker.patch("svs_core.users.user.SystemUserManager.create_user")
        """Test that deleting a template with associated services raises an
        error."""
        from svs_core.db.models import ServiceModel
        from svs_core.users.user import User

        template = Template.create(
            name="test-delete-with-services",
            type=TemplateType.IMAGE,
            image="nginx:latest",
            description="Template with services",
        )

        # Create a user for the service
        user = User.create(name="testuser", password="testpass123")

        # Create a service associated with this template
        service = ServiceModel.objects.create(
            name="test-service",
            template=template,
            user=user,
        )

        # Verify service exists
        assert ServiceModel.objects.filter(template=template).exists()

        # Attempt to delete the template
        with pytest.raises(
            Exception,
            match=f"Cannot delete template {template.name} as it is associated with existing services",
        ):
            template.delete()

        # Verify template still exists in database
        assert Template.objects.filter(id=template.id).exists()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_build_template(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.build_from_dockerfile"
        )
        mock_remove = mocker.patch("svs_core.docker.template.DockerImageManager.remove")
        dockerfile_content = "FROM alpine:latest\nRUN echo 'test'"

        template = Template.create(
            name="test-delete-build",
            type=TemplateType.BUILD,
            dockerfile=dockerfile_content,
            description="Build template to delete",
        )

        template_id = template.id

        # Verify template exists
        assert Template.objects.filter(id=template_id).exists()

        # Delete the template
        template.delete()

        # Verify template is deleted from database
        assert not Template.objects.filter(id=template_id).exists()

        # DockerImageManager.remove should not be called for build templates
        mock_remove.assert_not_called()
