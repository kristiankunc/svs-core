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
    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_success(
        self, create_network_mock, system_user_create_mock, db
    ):
        """Test creating a user with valid parameters."""

        username = "testuser"
        password = "password123"

        user = User.create(name=username, password=password)

        assert user.name == username
        assert User.get_by_name(username) is not None
        create_network_mock.assert_called_once_with(
            username, labels={"svs_user": username}
        )
        system_user_create_mock.assert_called_once_with(username, password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_duplicate(self, db):
        """Test creating a user with a duplicate username."""
        username = "dupeuser"
        password = "password123"
        User.create(name=username, password=password)
        with pytest.raises(AlreadyExistsException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_invalid_username(self, db):
        """Test creating a user with an invalid username."""
        username = "invalid@user"
        password = "password123"
        with pytest.raises(InvalidUsernameException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_invalid_password(self, db):
        """Test creating a user with an invalid password."""
        username = "validuser2"
        password = "short"
        with pytest.raises(InvalidPasswordException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_get_by_name(self, db):
        """Test retrieving a user by name."""
        username = "findme"
        password = "password123"
        User.create(name=username, password=password)
        user = User.get_by_name(username)

        assert user is not None
        assert user.name == username

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_check_password(self, db):
        """Test checking the password for a user."""
        username = "pwtest"
        password = "password123"
        user = User.create(name=username, password=password)

        assert user.check_password(password) is True
        assert user.check_password("wrongpass") is False
