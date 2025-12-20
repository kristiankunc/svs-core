from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Generator

import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import ServiceStatus, TemplateType
from svs_core.docker.json_properties import (
    DefaultContent,
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
def test_template(mocker: MockerFixture) -> Generator[Template, None, None]:
    mocker.patch(
        "svs_core.docker.template.DockerImageManager.exists", return_value=True
    )
    mocker.patch("svs_core.docker.template.DockerImageManager.pull")

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
            Volume(host_path="/tmp/nginx", container_path="/usr/share/nginx/html")
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
def test_user(mocker: MockerFixture) -> Generator[User, None, None]:
    mocker.patch("svs_core.users.user.DockerNetworkManager.create_network")
    mocker.patch("svs_core.users.user.SystemUserManager.create_user")

    user = User.create(name="testuser", password="password123")
    yield user


class TestService:
    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_create(
        self, mocker: MockerFixture, test_template: Any, test_user: Any
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_id"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

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
        print(mock_create_container.call_args.kwargs["ports"][0].container_port)
        call_args = mock_create_container.call_args[1]
        assert call_args["name"] == f"svs-{service.id}"
        assert call_args["image"] == "nginx:latest"
        assert call_args["command"] == "nginx -g 'daemon off;'"
        assert call_args["args"] == ["--no-cache"]
        assert len(call_args["ports"]) == 1
        assert call_args["ports"][0].container_port == 80
        assert call_args["ports"][0].host_port == 8080

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
    def test_service_create_from_template(
        self,
        mocker: MockerFixture,
        test_template: Any,
        test_user: Any,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_from_template"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock volume generation
        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume = mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        # Mock port finding
        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000
        )

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
    def test_service_env_merge_overwrites_template_values(
        self,
        mocker: MockerFixture,
        test_template: Any,
        test_user: Any,
    ) -> None:
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume = mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000
        )

        # Override an existing template env var (NGINX_PORT)
        service = Service.create_from_template(
            name="env-merge-test",
            template_id=test_template.id,
            user=test_user,
            override_env=[
                # Override template's 80
                EnvVariable(key="NGINX_PORT", value="8080"),
                EnvVariable(key="NEW_VAR", value="new_value"),  # New var
            ],
        )

        env_dict = {env.key: env.value for env in service.env}

        # Verify override took precedence
        assert env_dict["NGINX_PORT"] == "8080"
        # Verify new var added
        assert env_dict["NEW_VAR"] == "new_value"
        # Verify other template vars preserved
        assert env_dict["NGINX_HOST"] == "localhost"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_port_merge_overwrites_template_ports(
        self,
        mocker: MockerFixture,
        test_template: Any,
        test_user: Any,
    ) -> None:
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume = mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000
        )

        # Override existing template port (80)
        service = Service.create_from_template(
            name="port-merge-test",
            template_id=test_template.id,
            user=test_user,
            override_ports=[
                ExposedPort(
                    host_port=8080, container_port=80
                ),  # Override template's 80
                ExposedPort(host_port=8443, container_port=443),  # New port
            ],
        )

        ports_dict = {
            port.container_port: port.host_port for port in service.exposed_ports
        }

        # Verify override took precedence
        assert ports_dict[80] == 8080
        # Verify new port added
        assert ports_dict[443] == 8443

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_volume_merge_overwrites_template_volumes(
        self,
        mocker: MockerFixture,
        test_template: Any,
        test_user: Any,
    ) -> None:
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume = mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000
        )

        # Override existing template volume
        service = Service.create_from_template(
            name="volume-merge-test",
            template_id=test_template.id,
            user=test_user,
            override_volumes=[
                Volume(
                    host_path="/custom/nginx",
                    container_path="/usr/share/nginx/html",
                ),  # Override template's /tmp/nginx
                Volume(
                    host_path="/config", container_path="/etc/nginx/conf.d"
                ),  # New volume
            ],
        )

        volumes_dict = {vol.container_path: vol.host_path for vol in service.volumes}

        # Verify override took precedence
        assert volumes_dict["/usr/share/nginx/html"] == "/custom/nginx"
        # Verify new volume added
        assert volumes_dict["/etc/nginx/conf.d"] == "/config"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_label_merge_overwrites_template_labels(
        self,
        mocker: MockerFixture,
        test_template: Any,
        test_user: Any,
    ) -> None:
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mock_generate_volume = mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=9000
        )

        # Override existing template label
        service = Service.create_from_template(
            name="label-merge-test",
            template_id=test_template.id,
            user=test_user,
            override_labels=[
                Label(key="version", value="2.0"),  # Override template's 1.0
                Label(key="environment", value="staging"),  # New label
            ],
        )

        labels_dict = {label.key: label.value for label in service.labels}

        # Verify override took precedence
        assert labels_dict["version"] == "2.0"
        # Verify new label added
        assert labels_dict["environment"] == "staging"
        # Verify other template labels preserved
        assert labels_dict["app"] == "nginx"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_lifecycle(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "lifecycle_container_id"
        mock_container.status = "created"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_get_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

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

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_get_logs(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "logs_container_id"
        mock_container.status = "running"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_get_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock logs output
        log_content = b"2025-01-01T10:00:00Z Starting service...\n2025-01-01T10:00:01Z Service ready\n"
        mock_container.logs.return_value = log_content

        # Create service
        service = Service.create(
            name="log-test-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        # Retrieve logs
        logs = service.get_logs()

        # Verify container.logs() was called
        mock_get_container.assert_called_with("logs_container_id")
        mock_container.logs.assert_called_once_with(tail=1000)

        # Verify logs content
        assert isinstance(logs, str)
        assert "Starting service..." in logs
        assert "Service ready" in logs
        assert logs == log_content.decode("utf-8")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_get_logs_custom_tail(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "logs_container_id"
        mock_container.status = "running"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_get_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock logs output
        log_content = b"Log line 1\nLog line 2\nLog line 3\n"
        mock_container.logs.return_value = log_content

        # Create service
        service = Service.create(
            name="log-tail-test-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        # Retrieve last 50 lines
        logs = service.get_logs(tail=50)

        # Verify container.logs() was called with correct tail parameter
        mock_container.logs.assert_called_once_with(tail=50)

        # Verify logs content
        assert isinstance(logs, str)
        assert logs == log_content.decode("utf-8")

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_get_logs_no_container_id(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        mocker.patch("svs_core.docker.service.DockerContainerManager.create_container")
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )
        # Create service but manually clear container_id to simulate edge case
        service = Service.objects.create(
            name="no-container-id-service",
            template_id=test_template.id,
            user_id=test_user.id,
            image="nginx:alpine",
            container_id=None,
        )

        # Attempt to get logs should raise ValueError
        with pytest.raises(ValueError, match="Service does not have a container ID"):
            service.get_logs()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_get_logs_container_not_found(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "logs_container_id"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )

        # Mock container not found
        mock_get_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=None,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create service
        service = Service.create(
            name="container-not-found-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        # Attempt to get logs should raise ValueError
        with pytest.raises(ValueError, match="Container with ID .* not found"):
            service.get_logs()

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_get_logs_empty_logs(
        self,
        mocker: MockerFixture,
        test_template: Template,
        test_user: User,
    ) -> None:
        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "logs_container_id"
        mock_container.status = "running"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_get_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock empty logs
        mock_container.logs.return_value = b""

        # Create service
        service = Service.create(
            name="empty-logs-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        # Retrieve logs
        logs = service.get_logs()

        # Verify empty string returned
        assert logs == ""
        mock_container.logs.assert_called_once_with(tail=1000)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_create_writes_default_contents_to_volume(
        self,
        mocker: MockerFixture,
        test_user: User,
        tmp_path: Any,
    ) -> None:
        """Test that creating a service writes default contents to volumes."""
        # Mock Docker operations
        mocker.patch(
            "svs_core.docker.template.DockerImageManager.exists", return_value=True
        )
        mocker.patch("svs_core.docker.template.DockerImageManager.pull")

        # Create a template with default contents
        test_template = Template.create(
            name="nginx-with-config",
            type=TemplateType.IMAGE,
            image="nginx:alpine",
            description="Nginx with default config",
            default_volumes=[
                Volume(host_path=None, container_path="/etc/nginx/conf.d")
            ],
            default_contents=[
                DefaultContent(
                    location="/etc/nginx/conf.d/default.conf",
                    content="server { listen 80; }",
                )
            ],
            start_cmd="nginx -g 'daemon off;'",
        )

        # Mock container creation
        mock_container = mocker.MagicMock()
        mock_container.id = "default_content_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock volume path finding
        mock_volume_path = tmp_path / "volumes" / "user_123" / "vol1"
        mock_volume_path.mkdir(parents=True, exist_ok=True)
        config_file_path = (
            mock_volume_path / "etc" / "nginx" / "conf.d" / "default.conf"
        )

        mock_find_host_path = mocker.patch(
            "svs_core.docker.service.SystemVolumeManager.find_host_path",
            return_value=config_file_path,
        )

        # Mock write_to_host to avoid actual file writing
        mock_write_to_host = mocker.patch(
            "svs_core.docker.json_properties.DefaultContent.write_to_host"
        )

        # Create service with volumes
        service = Service.create(
            name="default-content-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
            volumes=[
                Volume(
                    host_path=str(mock_volume_path),
                    container_path="/etc/nginx/conf.d",
                )
            ],
        )

        # Verify find_host_path was called with the correct parameters
        mock_find_host_path.assert_called()

        # Verify write_to_host was called with the config file path
        mock_write_to_host.assert_called()

        # Verify the service was created
        assert service.id is not None
        assert service.name == "default-content-service"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_domain_stored_in_database(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that domain is properly stored in the database."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_domain"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service with domain
        service = Service.create(
            name="domain-test-service",
            template_id=test_template.id,
            user=test_user,
            domain="db-test.example.com",
            image="nginx:alpine",
        )

        # Verify domain is stored
        assert service.domain == "db-test.example.com"

        # Fetch from database and verify persistence
        fetched_service = Service.objects.get(id=service.id)
        assert fetched_service.domain == "db-test.example.com"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_without_domain_stored_as_none(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that services without domain have None stored in database."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_no_domain"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service without domain
        service = Service.create(
            name="no-domain-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
        )

        # Verify domain is None
        assert service.domain is None

        # Fetch from database and verify
        fetched_service = Service.objects.get(id=service.id)
        assert fetched_service.domain is None

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_domain_in_string_representation(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that domain appears in the string representation of Service."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_str"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service with domain
        service = Service.create(
            name="str-test-service",
            template_id=test_template.id,
            user=test_user,
            domain="str-test.example.com",
            image="nginx:alpine",
        )

        # Verify domain appears in string representation
        service_str = str(service)
        assert "domain=str-test.example.com" in service_str

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_domain_creates_labels_and_network_connection(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that domain is properly handled by creating labels and
        connecting to caddy network."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_passed"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_connect_network = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service with domain
        Service.create(
            name="pass-test-service",
            template_id=test_template.id,
            user=test_user,
            domain="pass-test.example.com",
            image="nginx:alpine",
            exposed_ports=[ExposedPort(host_port=80, container_port=80)],
        )

        # Verify caddy labels were passed to create_container
        mock_create_container.assert_called_once()
        call_kwargs = mock_create_container.call_args[1]
        labels = call_kwargs["labels"]

        # Check for caddy labels
        caddy_label = next((l for l in labels if l.key == "caddy"), None)
        reverse_proxy_label = next(
            (l for l in labels if l.key == "caddy.reverse_proxy"), None
        )

        assert caddy_label is not None
        assert caddy_label.value == "pass-test.example.com"
        assert reverse_proxy_label is not None
        assert reverse_proxy_label.value == "{{upstreams 80}}"

        # Verify network connections were made (user network + caddy network)
        assert mock_connect_network.call_count == 2
        calls = mock_connect_network.call_args_list
        # First call should be to user network
        assert calls[0][0][1] == test_user.name
        # Second call should be to caddy network
        assert calls[1][0][1] == "caddy"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_domain_creates_caddy_label(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that service with domain gets caddy label added."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_caddy_label"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service with domain
        service = Service.create(
            name="caddy-label-service",
            template_id=test_template.id,
            user=test_user,
            domain="caddy-label.example.com",
            image="nginx:alpine",
            exposed_ports=[ExposedPort(host_port=80, container_port=80)],
        )

        # Verify caddy label was added to the labels
        caddy_labels = [label for label in service.labels if label.key == "caddy"]
        assert len(caddy_labels) == 1
        assert caddy_labels[0].value == "caddy-label.example.com"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_from_template_with_domain(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that create_from_template properly handles domain parameter."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_from_template"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_connect_network = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock port finding
        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=8080
        )

        # Create service from template with domain
        service = Service.create_from_template(
            name="template-domain-service",
            template_id=test_template.id,
            user=test_user,
            domain="template-domain.example.com",
        )

        # Verify domain was set on the service
        assert service.domain == "template-domain.example.com"

        # Verify caddy labels were passed to create_container
        mock_create_container.assert_called_once()
        call_kwargs = mock_create_container.call_args[1]
        labels = call_kwargs["labels"]

        # Check for caddy labels
        caddy_label = next((l for l in labels if l.key == "caddy"), None)
        reverse_proxy_label = next(
            (l for l in labels if l.key == "caddy.reverse_proxy"), None
        )

        assert caddy_label is not None
        assert caddy_label.value == "template-domain.example.com"
        assert reverse_proxy_label is not None
        assert reverse_proxy_label.value == "{{upstreams 80}}"

        # Verify network connections were made
        assert mock_connect_network.call_count == 2

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_without_domain_no_caddy_labels(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that service without domain does NOT get caddy labels or
        network connection."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_no_caddy"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_connect_network = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service without domain
        Service.create(
            name="no-caddy-service",
            template_id=test_template.id,
            user=test_user,
            image="nginx:alpine",
            exposed_ports=[ExposedPort(host_port=80, container_port=80)],
        )

        # Verify caddy labels were NOT passed to create_container
        mock_create_container.assert_called_once()
        call_kwargs = mock_create_container.call_args[1]
        labels = call_kwargs["labels"]

        # Check that no caddy labels exist
        caddy_labels = [l for l in labels if l.key.startswith("caddy")]
        assert len(caddy_labels) == 0

        # Verify only user network connection was made (not caddy network)
        assert mock_connect_network.call_count == 1
        calls = mock_connect_network.call_args_list
        assert calls[0][0][1] == test_user.name

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_reverse_proxy_label_format(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that reverse proxy label has correct format without quotes."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_reverse_proxy"
        mock_create_container = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create a service with domain
        Service.create(
            name="reverse-proxy-service",
            template_id=test_template.id,
            user=test_user,
            domain="reverse-proxy.example.com",
            image="nginx:alpine",
            exposed_ports=[ExposedPort(host_port=80, container_port=80)],
        )

        # Verify reverse_proxy label format
        mock_create_container.assert_called_once()
        call_kwargs = mock_create_container.call_args[1]
        labels = call_kwargs["labels"]

        reverse_proxy_label = next(
            (l for l in labels if l.key == "caddy.reverse_proxy"), None
        )

        # Label should exist and have correct format (without quotes)
        assert reverse_proxy_label is not None
        assert reverse_proxy_label.value == "{{upstreams 80}}"
        # Verify it doesn't have surrounding quotes
        assert not reverse_proxy_label.value.startswith('"')
        assert not reverse_proxy_label.value.endswith('"')

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_caddy_network_connection_only_with_domain(
        self, test_template: Template, test_user: User, mocker: MockerFixture
    ) -> None:
        """Test that caddy network is only connected when domain is present."""
        mock_container = mocker.MagicMock()
        mock_container.id = "test_container_caddy_network"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mock_connect_network = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Create service with domain
        Service.create(
            name="caddy-network-service",
            template_id=test_template.id,
            user=test_user,
            domain="caddy-network.example.com",
            image="nginx:alpine",
            exposed_ports=[ExposedPort(host_port=80, container_port=80)],
        )

        # Verify caddy network connection was made
        assert mock_connect_network.call_count == 2
        calls = mock_connect_network.call_args_list
        network_names = [call[0][1] for call in calls]

        # Should connect to both user network and caddy network
        assert test_user.name in network_names
        assert "caddy" in network_names

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_service_build_with_build_args(
        self, mocker: MockerFixture, test_user: User
    ) -> None:
        """Test that build args are passed correctly when building service
        images."""
        # Create a BUILD template with build args
        build_template = Template.create(
            name="test-build-args",
            type=TemplateType.BUILD,
            dockerfile="""FROM busybox:latest
ARG APP_NAME
ARG APP_VERSION=1.0
RUN echo "APP_NAME=${APP_NAME}" > /app_info.txt
RUN echo "APP_VERSION=${APP_VERSION}" >> /app_info.txt
""",
            description="Test template with build args",
            default_env=[
                EnvVariable(key="APP_NAME", value="myapp"),
                EnvVariable(key="APP_VERSION", value="2.0"),
            ],
        )

        # Mock container operations
        mock_container = mocker.MagicMock()
        mock_container.id = "build_args_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock the actual image building
        mock_build = mocker.patch(
            "svs_core.docker.service.DockerImageManager.build_from_dockerfile"
        )

        # Create a temporary directory to simulate source path
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir)

            # Create service with custom env vars
            service = Service.create(
                name="build-args-service",
                template_id=build_template.id,
                user=test_user,
                env=[
                    EnvVariable(key="APP_NAME", value="custom_app"),
                    EnvVariable(key="APP_VERSION", value="3.0"),
                ],
            )

            # Build the image
            service.build(source_path)

            # Verify build_from_dockerfile was called with correct build_args
            mock_build.assert_called_once()
            call_args = mock_build.call_args

            # Check that build_args parameter was passed
            assert "build_args" in call_args.kwargs
            build_args = call_args.kwargs["build_args"]

            # Verify build args contain the env variables
            assert build_args["APP_NAME"] == "custom_app"
            assert build_args["APP_VERSION"] == "3.0"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_django_template_build_args(
        self, mocker: MockerFixture, test_user: User
    ) -> None:
        """Test Django template with APP_NAME build arg."""
        # Load the actual Django template
        django_template = Template.import_from_json(
            {
                "name": "django-app",
                "type": "build",
                "description": "Django application container built on-demand from source",
                "dockerfile": """FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \\
    && pip install -r requirements.txt gunicorn

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/tmp

ARG APP_NAME=
ENV APP_NAME=${APP_NAME}

RUN if [ -z "$APP_NAME" ]; then echo "APP_NAME argument is required" >&2; exit 1; fi

RUN groupadd -r appuser && useradd -r -g appuser appuser

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app
COPY . .

RUN mkdir -p /app && chmod -R 777 /app \\
    && python manage.py collectstatic --noinput || true

EXPOSE 8000

USER appuser

CMD ["sh", "-c", "/usr/local/bin/gunicorn --bind 0.0.0.0:8000 --workers 3 ${APP_NAME}.wsgi"]
""",
                "default_env": [
                    {"key": "DEBUG", "value": "False"},
                    {"key": "SECRET_KEY", "value": ""},
                    {"key": "APP_NAME", "value": ""},
                ],
                "default_ports": [{"container": 8000, "host": None}],
                "default_volumes": [{"container": "/app/data", "host": None}],
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:8000/"],
                    "interval": 30,
                    "timeout": 10,
                    "retries": 3,
                    "start_period": 5,
                },
            }
        )

        # Mock container operations
        mock_container = mocker.MagicMock()
        mock_container.id = "django_build_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock volume generation
        mock_volume_path = mocker.MagicMock()
        mock_volume_path.as_posix.return_value = "/tmp/generated-volume"
        mocker.patch(
            "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
            return_value=mock_volume_path,
        )

        # Mock port finding
        mocker.patch(
            "svs_core.shared.ports.SystemPortManager.find_free_port", return_value=8000
        )

        # Mock the actual image building
        mock_build = mocker.patch(
            "svs_core.docker.service.DockerImageManager.build_from_dockerfile"
        )

        # Create a temporary directory to simulate Django project
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir)

            # Create dummy requirements.txt
            (source_path / "requirements.txt").write_text("Django==5.0\n")

            # Create service with Django-specific env vars
            service = Service.create(
                name="django-service",
                template_id=django_template.id,
                user=test_user,
                env=[
                    EnvVariable(key="DEBUG", value="False"),
                    EnvVariable(key="SECRET_KEY", value="super-secret-key-123"),
                    EnvVariable(key="APP_NAME", value="myproject"),
                ],
            )

            # Build the image
            service.build(source_path)

            # Verify build_from_dockerfile was called with APP_NAME build arg
            mock_build.assert_called_once()
            call_args = mock_build.call_args

            # Check build_args were passed
            assert "build_args" in call_args.kwargs
            build_args = call_args.kwargs["build_args"]

            # Verify APP_NAME is in build args
            assert "APP_NAME" in build_args
            assert build_args["APP_NAME"] == "myproject"

            # Verify other env vars are also passed as build args
            assert build_args["DEBUG"] == "False"
            assert build_args["SECRET_KEY"] == "super-secret-key-123"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_django_template_default_env_values(
        self, mocker: MockerFixture, test_user: User
    ) -> None:
        """Test that Django template has correct default environment
        variables."""
        # Load the actual Django template from file
        import json
        import os

        template_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "service_templates",
            "django.json",
        )

        with open(template_path, "r") as f:
            django_json = json.load(f)

        template = Template.import_from_json(django_json)

        # Verify default environment variables
        env_dict = {env.key: env.value for env in template.default_env}

        # Check DEBUG is False by default (not True)
        assert "DEBUG" in env_dict
        assert env_dict["DEBUG"] == "False"

        # Check SECRET_KEY exists (even if empty)
        assert "SECRET_KEY" in env_dict

        # Check APP_NAME exists (even if empty)
        assert "APP_NAME" in env_dict

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_django_template_dockerfile_has_app_name_arg(
        self, mocker: MockerFixture
    ) -> None:
        """Test that Django template Dockerfile includes APP_NAME ARG."""
        import json
        import os

        template_path = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            ),
            "service_templates",
            "django.json",
        )

        with open(template_path, "r") as f:
            django_json = json.load(f)

        template = Template.import_from_json(django_json)

        # Verify Dockerfile contains APP_NAME ARG
        assert template.dockerfile is not None
        assert "ARG APP_NAME=" in template.dockerfile
        assert "ENV APP_NAME=${APP_NAME}" in template.dockerfile

        # Verify the gunicorn CMD uses APP_NAME
        assert "${APP_NAME}.wsgi" in template.dockerfile

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_build_template_without_build_args(
        self, mocker: MockerFixture, test_user: User
    ) -> None:
        """Test that templates without build args still work correctly."""
        # Create a simple BUILD template without any ARG instructions
        simple_template = Template.create(
            name="simple-build",
            type=TemplateType.BUILD,
            dockerfile="""FROM busybox:latest
RUN echo "Simple build" > /message.txt
CMD cat /message.txt
""",
            description="Simple template without build args",
        )

        # Mock container operations
        mock_container = mocker.MagicMock()
        mock_container.id = "simple_build_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Mock the actual image building
        mock_build = mocker.patch(
            "svs_core.docker.service.DockerImageManager.build_from_dockerfile"
        )

        # Create service without env vars
        service = Service.create(
            name="simple-service",
            template_id=simple_template.id,
            user=test_user,
        )

        # Build the image
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir)
            service.build(source_path)

            # Verify build was called
            mock_build.assert_called_once()
            call_args = mock_build.call_args

            # Build args should still be passed (empty dict)
            assert "build_args" in call_args.kwargs

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_build_service_deletes_image_when_deleted(
        self, mocker: MockerFixture, test_user: User
    ) -> None:
        """Test that building a service creates an image that is deleted when
        the service is deleted."""
        # Create a BUILD template
        build_template = Template.create(
            name="deletion-build-template",
            type=TemplateType.BUILD,
            dockerfile="""FROM busybox:latest
RUN echo "To be deleted" > /to_be_deleted.txt
CMD cat /to_be_deleted.txt
""",
            description="Template for testing image deletion",
        )

        # Mock container operations
        mock_container = mocker.MagicMock()
        mock_container.id = "deletion_build_container"
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.create_container",
            return_value=mock_container,
        )

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )
        # Mock the actual image building
        mock_build = mocker.patch(
            "svs_core.docker.service.DockerImageManager.build_from_dockerfile",
            return_value="deletion_build_image_id",
        )

        # Mock image deletion
        mock_delete_image = mocker.patch(
            "svs_core.docker.service.DockerImageManager.delete"
        )

        # Create service
        service = Service.create(
            name="deletion-service",
            template_id=build_template.id,
            user=test_user,
        )

        # Build the image
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir)
            service.build(source_path)

            # Verify build was called
            mock_build.assert_called_once()

        # Delete the service
        service.delete()
