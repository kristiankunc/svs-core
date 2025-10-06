import pytest

from pytest_mock import MockerFixture

from svs_core.docker.network import DockerNetworkManager
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException, User


@pytest.fixture(autouse=True)
def create_network_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "svs_core.docker.network.DockerNetworkManager.create_network",
        return_value=None,
    )


@pytest.fixture(autouse=True)
def system_user_create_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )


@pytest.fixture(autouse=True)
def system_user_delete_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )


class TestUserIntegration:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_user_success(
        self, create_network_mock, system_user_create_mock
    ):
        """Test creating a user with valid parameters."""

        username = "testuser"
        password = "password123"

        user = await User.create(name=username, password=password)

        assert user.name == username
        assert await User.get_by_name(username) is not None
        create_network_mock.assert_called_once_with(
            username, labels={"svs_user": username}
        )
        system_user_create_mock.assert_called_once_with(username, password)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_user_duplicate(self):
        """Test creating a user with a duplicate username."""
        username = "dupeuser"
        password = "password123"
        await User.create(name=username, password=password)
        with pytest.raises(AlreadyExistsException):
            await User.create(name=username, password=password)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_user_invalid_username(self):
        """Test creating a user with an invalid username."""
        username = "invalid@user"
        password = "password123"
        with pytest.raises(InvalidUsernameException):
            await User.create(name=username, password=password)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_user_invalid_password(self):
        """Test creating a user with an invalid password."""
        username = "validuser2"
        password = "short"
        with pytest.raises(InvalidPasswordException):
            await User.create(name=username, password=password)

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_get_by_name(self):
        """Test retrieving a user by name."""
        username = "findme"
        password = "password123"
        await User.create(name=username, password=password)
        user = await User.get_by_name(username)

        assert user is not None
        assert user.name == username

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_check_password(self):
        """Test checking the password for a user."""
        username = "pwtest"
        password = "password123"
        user = await User.create(name=username, password=password)

        assert await user.check_password(password) is True
        assert await user.check_password("wrongpass") is False
