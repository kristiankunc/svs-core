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
