from pathlib import Path

import pytest

from svs_core.docker.network import DockerNetworkManager


@pytest.fixture
def db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        yield


@pytest.fixture()
def mock_system_user_manager(mocker):
    mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


@pytest.fixture
def mock_system_user_create(mocker):
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )


@pytest.fixture
def mock_system_user_delete(mocker):
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


@pytest.fixture
def mock_docker_network_create(mocker):
    return mocker.patch(
        "svs_core.docker.network.DockerNetworkManager.create_network",
        return_value=None,
    )


@pytest.fixture
def mock_docker_network_delete(mocker):
    return mocker.patch(
        "svs_core.docker.network.DockerNetworkManager.delete_network",
        return_value=None,
    )


@pytest.fixture
def mock_volume_delete(mocker):
    return mocker.patch(
        "svs_core.shared.volumes.SystemVolumeManager.delete_user_volumes",
        return_value=None,
    )


@pytest.fixture
def mock_docker_image_pull(mocker):
    return mocker.patch(
        "svs_core.docker.image.DockerImageManager.pull",
        return_value=None,
    )


@pytest.fixture
def mock_docker_image_exists(mocker):
    return mocker.patch(
        "svs_core.docker.image.DockerImageManager.exists",
        return_value=True,
    )


@pytest.fixture
def mock_docker_container_create(mocker):
    mock_container = mocker.MagicMock()
    mock_container.id = "test_container_id"
    mock_container.name = "test_container"
    mock_container.status = "created"
    return mocker.patch(
        "svs_core.docker.container.DockerContainerManager.create_container",
        return_value=mock_container,
    )


@pytest.fixture
def mock_run_command(mocker):
    return mocker.patch(
        "svs_core.shared.shell.run_command",
        return_value=mocker.MagicMock(returncode=0, stdout="", stderr=""),
    )


@pytest.fixture
def docker_cleanup(db):
    from svs_core.docker.container import DockerContainerManager
    from svs_core.docker.image import DockerImageManager

    yield

    for image in DockerImageManager.get_all():
        image_name = image.tags[0].split(":")[0] if image.tags else None
        if image and image_name and image.labels.get("svs") == "true":
            print("Cleaning up image:", image_name)
            DockerImageManager.remove(image_name)

    for container in DockerContainerManager.get_all():
        if container and container.labels.get("svs_user") is not None:
            print("Cleaning up container:", container.name)
            DockerContainerManager.remove(container.id)

    for network in DockerNetworkManager.get_networks():
        labels = network.attrs.get("Labels", {})
        if labels.get("svs") == "true":
            print("Cleaning up network:", network.name)
            DockerNetworkManager.delete_network(network.id)
