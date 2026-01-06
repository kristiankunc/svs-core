"""Common fixtures for integration tests."""

from typing import Generator

import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import TemplateType
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Healthcheck,
    Label,
    Volume,
)
from svs_core.docker.template import Template
from svs_core.users.user import User


@pytest.fixture
def test_template(mocker: MockerFixture) -> Generator[Template, None, None]:
    """Create a test template for integration tests."""
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
def test_user(
    mocker: MockerFixture,
    mock_docker_network_create: object,
    mock_system_user_create: object,
) -> Generator[User, None, None]:
    """Create a test user for integration tests."""
    user = User.create(name="testuser", password="password123")
    yield user


@pytest.fixture
def mock_system_user_create(mocker: MockerFixture) -> object:
    """Mock SystemUserManager.create_user for integration tests."""
    return mocker.patch(
        "svs_core.users.user.SystemUserManager.create_user",
        return_value=None,
    )


@pytest.fixture
def mock_system_user_delete(mocker: MockerFixture) -> object:
    """Mock SystemUserManager.delete_user for integration tests."""
    return mocker.patch(
        "svs_core.users.user.SystemUserManager.delete_user",
        return_value=None,
    )


@pytest.fixture
def mock_docker_network_create(mocker: MockerFixture) -> object:
    """Mock DockerNetworkManager.create_network for integration tests."""
    return mocker.patch(
        "svs_core.users.user.DockerNetworkManager.create_network",
        return_value=None,
    )


@pytest.fixture
def mock_docker_network_delete(mocker: MockerFixture) -> object:
    """Mock DockerNetworkManager.delete_network for integration tests."""
    return mocker.patch(
        "svs_core.users.user.DockerNetworkManager.delete_network",
        return_value=None,
    )


@pytest.fixture
def mock_volume_delete(mocker: MockerFixture) -> object:
    """Mock SystemVolumeManager.delete_user_volumes for integration tests."""
    return mocker.patch(
        "svs_core.users.user.SystemVolumeManager.delete_user_volumes",
        return_value=None,
    )


@pytest.fixture
def mock_service_container(mocker: MockerFixture) -> object:
    """Mock Docker container operations for Service integration tests.

    This fixture provides:
    - A mock container object with configurable id
    - Mocked DockerContainerManager.create_container
    - Mocked DockerContainerManager.connect_to_network

    Returns the mock container object for further configuration in tests.
    """
    mock_container = mocker.MagicMock()
    mock_container.id = "test_container_id"
    mock_container.status = "created"

    mocker.patch(
        "svs_core.docker.service.DockerContainerManager.create_container",
        return_value=mock_container,
    )
    mocker.patch("svs_core.docker.service.DockerContainerManager.connect_to_network")

    return mock_container


@pytest.fixture
def test_service(
    mocker: MockerFixture,
    test_template: Template,
    test_user: User,
    mock_service_container: object,
) -> object:
    """Create a test service for integration tests.

    This fixture provides a fully configured Service instance with:
    - Associated template (test_template)
    - Associated user (test_user)
    - Mocked Docker container operations
    - Default configuration (name, domain, image, ports, env, volumes, etc.)

    Additional mocks provided:
    - SystemVolumeManager.generate_free_volume (returns /tmp/test-volume)
    - SystemPortManager.find_free_port (returns 8080)

    Returns the created Service instance.
    """
    from svs_core.docker.service import Service

    # Mock volume generation for tests that use create_from_template
    mock_volume_path = mocker.MagicMock()
    mock_volume_path.as_posix.return_value = "/tmp/test-volume"
    mocker.patch(
        "svs_core.shared.volumes.SystemVolumeManager.generate_free_volume",
        return_value=mock_volume_path,
    )

    # Mock port finding for tests that use create_from_template
    mocker.patch(
        "svs_core.shared.ports.SystemPortManager.find_free_port",
        return_value=8080,
    )

    # Create a service with standard test configuration
    service = Service.create(
        name="test-service",
        template_id=test_template.id,
        user=test_user,
        domain="test.example.com",
        image="nginx:alpine",
        exposed_ports=[ExposedPort(host_port=8080, container_port=80)],
        env=[
            EnvVariable(key="TEST_ENV", value="test_value"),
        ],
        volumes=[Volume(host_path="/tmp/test", container_path="/usr/share/nginx/html")],
        command="nginx -g 'daemon off;'",
        healthcheck=Healthcheck(
            test=["CMD", "curl", "-f", "http://localhost"],
        ),
        labels=[Label(key="environment", value="test")],
        args=["--test-arg"],
    )

    return service
