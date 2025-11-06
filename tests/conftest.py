from pathlib import Path

import pytest

from svs_core.docker.network import DockerNetworkManager
from svs_core.users.user import User


@pytest.fixture
def db(django_db_setup, django_db_blocker):
    """Ensure the database is set up for the test."""
    with django_db_blocker.unblock():
        yield


@pytest.fixture
def svs_user(db, mocker, tmp_path, request):
    mocker.patch("svs_core.docker.network.DockerNetworkManager.create_network")
    mocker.patch("svs_core.docker.network.DockerNetworkManager.delete_network")
    mocker.patch(
        "svs_core.users.user.SystemUserManager.is_user_in_group", return_value=False)

    user = User.create("testuser", "12345678")

    yield user

    try:
        user.delete()
    except Exception as e:
        user_still_exists = User.objects.filter(name=user.name).exists()
        if user_still_exists:
            print(f"Warning: Failed to delete user during cleanup: {user}", e)


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
