import pytest

from svs_core.docker.network import DockerNetworkManager


@pytest.fixture
def db(django_db_setup, django_db_blocker):
    """Ensure the database is set up for the test."""
    with django_db_blocker.unblock():
        yield


@pytest.fixture(autouse=True)
def mock_system_user_manager(mocker):
    """Mock system user manager to prevent system calls during tests."""
    mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


@pytest.fixture
def docker_cleanup(db):
    """Cleanup Docker containers and images after each test.

    This fixture now also accepts the db fixture to ensure database
    access.
    """
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
