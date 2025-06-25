import pytest

from svs_core.users.user import User


class TestUser:
    @pytest.mark.unit
    def test_is_username_valid(self):
        """Test the username validation method of the User class."""
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
    def test_is_password_valid(self):
        """Test the password validation method of the User class."""
        assert User.is_password_valid("password123") is True
        assert User.is_password_valid("short") is False
        assert User.is_password_valid(12345678) is False  # type: ignore[arg-type]
        assert User.is_password_valid("") is False

    @pytest.mark.unit
    def test_exceptions(self):
        """Test the exception messages for user-related exceptions."""
        from svs_core.users.user import (
            InvalidPasswordException,
            InvalidUsernameException,
            UsernameAlreadyExistsException,
        )

        uname = "bad!user"
        upass = "short"
        assert str(InvalidUsernameException(uname)) == f"Invalid username: '{uname}'."
        assert (
            str(UsernameAlreadyExistsException(uname))
            == f"Username '{uname}' already exists."
        )
        assert (
            str(InvalidPasswordException(upass))
            == f"Invalid password: '{upass}'. Password must be at least 8 characters long."
        )
