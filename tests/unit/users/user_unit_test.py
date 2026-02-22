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
    def test_is_password_valid_boundary_conditions(self, db):
        """Test password validation at exact boundaries."""
        # 7 characters - should fail
        assert User.is_password_valid("1234567") is False
        # 8 characters - should pass (minimum)
        assert User.is_password_valid("12345678") is True
        # 9 characters - should pass
        assert User.is_password_valid("123456789") is True

    @pytest.mark.unit
    def test_is_password_valid_character_types(self, db):
        """Test password validation with various character types."""
        # All lowercase
        assert User.is_password_valid("abcdefgh") is True
        # All uppercase
        assert User.is_password_valid("ABCDEFGH") is True
        # All numbers
        assert User.is_password_valid("12345678") is True
        # Special characters
        assert User.is_password_valid("!@#$%^&*") is True
        # Mixed
        assert User.is_password_valid("P@ssw0rd") is True
        # Unicode
        assert User.is_password_valid("pässwörd") is True
        # Spaces
        assert User.is_password_valid("pass word") is True
        # Emoji (8 characters worth)
        assert User.is_password_valid("🔒🔑🔐🗝️🛡️🔓🔏🗝") is True

    @pytest.mark.unit
    def test_is_password_valid_type_checking(self, db):
        """Test password validation with invalid types."""
        assert User.is_password_valid(None) is False  # type: ignore[arg-type]
        assert User.is_password_valid(12345678) is False  # type: ignore[arg-type]
        assert User.is_password_valid(True) is False  # type: ignore[arg-type]
        assert User.is_password_valid([]) is False  # type: ignore[arg-type]
        assert User.is_password_valid({}) is False  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_is_password_valid_whitespace(self, db):
        """Test password validation with various whitespace."""
        # 8 spaces - should pass (though not recommended)
        assert User.is_password_valid("        ") is True
        # Tabs
        assert User.is_password_valid("\t\t\t\t\t\t\t\t") is True
        # Newlines
        assert User.is_password_valid("\n\n\n\n\n\n\n\n") is True
        # Mixed whitespace
        assert User.is_password_valid("  \t\n  \t\n") is True

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
            raise InvalidPasswordException()

    @pytest.mark.unit
    def test_change_password_valid(self, mocker):
        from svs_core.users.system import SystemUserManager

        mocker.patch("svs_core.users.user.hash_password", return_value=b"hashed")
        mock_change_password = mocker.patch.object(
            SystemUserManager, "change_user_password"
        )

        user = User(name="testuser", password="oldhash")
        mocker.patch.object(user, "save")

        user.change_password("newpassword123")

        assert user.password == "hashed"
        mock_change_password.assert_called_once_with("testuser", "newpassword123")

    @pytest.mark.unit
    def test_change_password_invalid_raises(self, mocker):
        from svs_core.users.user import InvalidPasswordException

        user = User(name="testuser", password="oldhash")

        with pytest.raises(InvalidPasswordException):
            user.change_password("short")
