import pytest

from svs_core.exceptions.base import AlreadyExistsException, InvalidOperationException
from svs_core.exceptions.user import (
    InvalidPasswordException,
    InvalidUsernameException,
)
from svs_core.shared.volumes import SystemVolumeManager
from svs_core.users.user import User


class TestUser:
    @pytest.mark.parametrize(
        "username, expected",
        [
            ("valid_user", True),
            ("a", True),
            ("_user", True),
            ("user123", True),
            ("user-name", True),
            ("user_name-123", True),
            ("user$", True),
            ("invalid user!", False),
            ("anotherValidUser123", False),  # Contains uppercase letters
            ("", False),  # Empty string
            ("user_with_@_symbol", False),  # Contains @
            ("123user", False),  # Starts with digit
            ("User_name", False),  # Starts with uppercase
            ("-user", False),  # Starts with hyphen
            ("a" * 33, False),  # Exceeds 32 character limit
            (1, False),  # Non-string input
        ],
    )
    def test_is_username_valid(self, username, expected):
        assert User.is_username_valid(username) == expected

    @pytest.mark.parametrize(
        "password, expected",
        [
            ("password", True),
            ("12345678", True),
            ("pass", False),
            ("", False),
            ("1234567", False),
            ("abcdefgh", True),
        ],
    )
    def test_is_password_valid(self, password, expected):
        """Test password validation logic."""

        assert User.is_password_valid(password) == expected

    @pytest.mark.django_db
    def test_create_user_success(self, mocker):
        mock_create_network = mocker.patch(
            "svs_core.docker.network.DockerNetworkManager.create_network"
        )
        mock_create_system_user = mocker.patch(
            "svs_core.users.user.SystemUserManager.create_user"
        )

        user = User.create(name="valid_user",
                           password="strongpassword", is_admin=False)

        assert user.name == "valid_user"
        assert user.is_admin() is False
        mock_create_network.assert_called_once_with(
            "valid_user", labels={"svs_user": "valid_user"})
        mock_create_system_user.assert_called_once_with(
            "valid_user", "strongpassword", False)

    @pytest.mark.django_db
    def test_create_user_invalid_username(self):
        with pytest.raises(InvalidUsernameException):
            User.create(name="Invalid User!", password="strongpassword")

    @pytest.mark.django_db
    def test_create_user_invalid_password(self):
        with pytest.raises(InvalidPasswordException):
            User.create(name="valid_user", password="short")

    @pytest.mark.django_db
    def test_create_user_already_exists(self, mocker):
        User.objects.create(
            name="existing_user", password="hashedpassword")

        with pytest.raises(AlreadyExistsException):
            User.create(name="existing_user", password="anotherpassword")

    @pytest.mark.django_db
    def test_check_password(self, svs_user):
        assert svs_user.check_password("12345678") is True
        assert svs_user.check_password("wrongpassword") is False

    @pytest.mark.django_db
    def test_delete_user(self, svs_user, mocker):
        mock_delete_network = mocker.patch(
            "svs_core.docker.network.DockerNetworkManager.delete_network"
        )
        mock_delete_system_user = mocker.patch(
            "svs_core.users.user.SystemUserManager.delete_user"
        )

        svs_user.delete()

        mock_delete_network.assert_called_once_with(svs_user.name)
        mock_delete_system_user.assert_called_once_with(svs_user.name)

    # TODO: add
    @pytest.mark.django_db
    def test_delete_user_with_existing_services(self, svs_user, mocker):
        pass
