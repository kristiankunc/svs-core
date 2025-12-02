import pytest

from pytest_mock import MockerFixture

from svs_core.users.user import User


class TestUser:
    @pytest.mark.unit
    def test_is_username_valid(self, db):
        valid_usernames = ["valid_user", "user123", "user-name", "user_name"]
        invalid_usernames = [
            "",
            "a" * 33,
            "1invalid",
            "invalid@name",
            "invalid name",
            "invalid$name",
        ]

        for username in valid_usernames:
            assert User.is_username_valid(username) is True

        for username in invalid_usernames:
            assert User.is_username_valid(username) is False

    @pytest.mark.unit
    def test_is_password_valid(self, db):
        assert User.is_password_valid("password123") is True
        assert User.is_password_valid("short") is False
        assert User.is_password_valid(12345678) is False  # type: ignore[arg-type]
        assert User.is_password_valid("") is False

    @pytest.mark.unit
    def test_exceptions(self, db):
        from svs_core.shared.exceptions import AlreadyExistsException
        from svs_core.users.user import (
            InvalidPasswordException,
            InvalidUsernameException,
        )

        uname = "bad!user"
        upass = "short"

        with pytest.raises(InvalidUsernameException):
            raise InvalidUsernameException(uname)

        with pytest.raises(AlreadyExistsException):
            raise AlreadyExistsException(entity="User", identifier=uname)

        with pytest.raises(InvalidPasswordException):
            raise InvalidPasswordException(upass)

    @pytest.mark.unit
    @pytest.mark.django_db
    def test_user_uid_property(self, mocker: MockerFixture) -> None:
        """Test that User.uid property calls SystemUserManager.get_uid()."""
        # Create a user instance without saving to DB
        user = User(id=1, name="testuser", password="hashed_password")

        # Mock the SystemUserManager.get_uid method
        mock_get_uid = mocker.patch(
            "svs_core.users.user.SystemUserManager.get_uid",
            return_value=1000,
        )

        # Access the uid property
        uid = user.uid

        # Verify the method was called with the correct username
        mock_get_uid.assert_called_once_with("testuser")
        assert uid == 1000

    @pytest.mark.unit
    @pytest.mark.django_db
    def test_user_gid_property(self, mocker: MockerFixture) -> None:
        """Test that User.gid property calls SystemUserManager.get_gid()."""
        # Create a user instance without saving to DB
        user = User(id=1, name="testuser", password="hashed_password")

        # Mock the SystemUserManager.get_gid method
        mock_get_gid = mocker.patch(
            "svs_core.users.user.SystemUserManager.get_gid",
            return_value=1000,
        )

        # Access the gid property
        gid = user.gid

        # Verify the method was called with the correct username
        mock_get_gid.assert_called_once_with("testuser")
        assert gid == 1000
