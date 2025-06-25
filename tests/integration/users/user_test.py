import pytest
from tortoise.contrib.test import TestCase

from svs_core.users.user import (
    InvalidPasswordException,
    InvalidUsernameException,
    User,
    UsernameAlreadyExistsException,
)


class TestUserIntegration(TestCase):
    async def test_create_user_success(self):
        """Test creating a user with valid parameters."""
        user = await User.create(name="testuser", password="password123")
        assert user.name == "testuser"
        assert await User.get_by_name("testuser") is not None

    async def test_create_user_duplicate(self):
        """Test creating a user with a duplicate username."""
        await User.create(name="dupeuser", password="password123")
        with pytest.raises(UsernameAlreadyExistsException):
            await User.create(name="dupeuser", password="password123")

    async def test_create_user_invalid_username(self):
        """Test creating a user with an invalid username."""
        with pytest.raises(InvalidUsernameException):
            await User.create(name="invalid@user", password="password123")

    async def test_create_user_invalid_password(self):
        """Test creating a user with an invalid password."""
        with pytest.raises(InvalidPasswordException):
            await User.create(name="validuser2", password="short")

    async def test_get_by_name(self):
        """Test retrieving a user by name."""
        await User.create(name="findme", password="password123")
        user = await User.get_by_name("findme")
        assert user is not None
        assert user.name == "findme"

    async def test_check_password(self):
        """Test checking the password for a user."""
        user = await User.create(name="pwtest", password="password123")
        assert await user.check_password("password123") is True
        assert await user.check_password("wrongpass") is False
