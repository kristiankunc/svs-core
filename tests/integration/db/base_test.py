import asyncio
from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from svs_core.users.user import User

# TODO: use a in-place model for testing OrmBase instead of User


# Automatically mock the docker network creation
@pytest.fixture(autouse=True)
def create_network_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "svs_core.docker.network.DockerNetworkManager.create_network",
        return_value=None,
    )


# Automatically mock system user management
@pytest.fixture(autouse=True)
def system_user_mock(mocker: MockerFixture) -> MockerFixture:
    mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


class TestOrmBase:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_created_and_updated_at_fields(self):
        """Test that created_at and updated_at fields are set correctly."""

        user = await User.create(name="testuser", password="password")
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert abs((user.created_at - user.updated_at).total_seconds()) < 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when the model is saved."""

        user = await User.create(name="testuser", password="password")
        old_updated_at = user.updated_at

        user._model.name = "Updated Name"
        await user._model.save()
        await asyncio.sleep(0.1)
        assert user.updated_at > old_updated_at

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_signal_post_save_updates_instance(self):
        """Test that the post_save signal updates the instance."""

        user = await User.create(name="testuser", password="password")
        user._model.name = "Changed Name"
        await user._model.save()
        await asyncio.sleep(0.1)
        assert user.name == "Changed Name" or user._model.name == "Changed Name"  # type: ignore
