import pytest

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
