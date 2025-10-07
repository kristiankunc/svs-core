import asyncio
import os

import pytest
import pytest_asyncio

from django.apps import apps
from django.conf import settings
from django.db import connection, connections, transaction
from psycopg import OperationalError
from pytest_mock import MockerFixture
from tortoise import Tortoise, connections

from svs_core.db.settings import setup_django
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.network import DockerNetworkManager

setup_django()


@pytest.fixture(scope="session", autouse=True)
def django_db_setup():
    """Ensure the Django database is set up for tests."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")

    from django.core.management import call_command

    call_command("migrate", verbosity=0, interactive=False)


@pytest.fixture(autouse=True)
def clean_db():
    """Clean database before each test."""
    with connection.cursor() as cursor:
        cursor.execute("TRUNCATE TABLE django_migrations RESTART IDENTITY CASCADE;")
        for model in apps.get_models():
            try:
                cursor.execute(
                    f"TRUNCATE TABLE {model._meta.db_table} RESTART IDENTITY CASCADE;"
                )
            except Exception as e:
                print(f"Could not truncate table {model._meta.db_table}: {e}")
    transaction.set_autocommit(True)


@pytest.fixture(autouse=True)
def mock_system_user_manager(mocker: MockerFixture) -> MockerFixture:
    """Automatically mock SystemUserManager methods to prevent actual system
    user creation/deletion."""
    mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


@pytest_asyncio.fixture
async def docker_cleanup():
    """Fixture to clean up Docker after each test.

    Removes all non-system containers and images. In development env,
    skips image removal.
    """
    yield

    ignored_images = ["postgres", "lucaslorentz/caddy-docker-proxy"]

    for image in DockerImageManager.get_all():
        image_name = image.tags[0].split(":")[0] if image.tags else None

        if os.getenv("ENVIRONMENT") == "dev":
            continue

        if image and image_name and not image in ignored_images:
            print(f"Removing image {image_name})")
            DockerImageManager.remove(image_name)

    for container in DockerContainerManager.get_all():
        if container and container.labels.get("svs_user") is not None:
            DockerContainerManager.remove(container.id)
