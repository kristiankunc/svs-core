import os

import pytest

from django.conf import settings

from svs_core.db.settings import setup_django

setup_django()


@pytest.fixture(scope="session")
def django_db_setup():
    """Override the django_db_setup fixture."""
    settings.MIGRATION_MODULES = {
        app.split(".")[-1]: None for app in settings.INSTALLED_APPS
    }


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


import os

import pytest_asyncio


@pytest_asyncio.fixture
async def docker_cleanup(db):
    """Cleanup Docker containers and images after each test.

    This fixture now also accepts the db fixture to ensure database
    access.
    """
    from svs_core.docker.container import DockerContainerManager
    from svs_core.docker.image import DockerImageManager

    yield

    for image in DockerImageManager.get_all():
        image_name = image.tags[0].split(":")[0] if image.tags else None
        if os.getenv("ENVIRONMENT") == "dev":
            continue
        if image and image_name and image.labels.get("svs") == "true":
            DockerImageManager.remove(image_name)

    for container in DockerContainerManager.get_all():
        if container and container.labels.get("svs_user") is not None:
            DockerContainerManager.remove(container.id)
