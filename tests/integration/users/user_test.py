import docker
import pytest
from tortoise.contrib.test import TestCase

from svs_core.docker.base import get_docker_client
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import (
    InvalidPasswordException,
    InvalidUsernameException,
    User,
)


class TestUserIntegration(TestCase):
    @pytest.mark.integration
    async def test_create_user_success(self):
        """Test creating a user with valid parameters."""

        user = await User.create(name="testuser", password="password123")

        assert user.name == "testuser"
        assert await User.get_by_name("testuser") is not None

        await user.delete()

    @pytest.mark.integration
    async def test_create_user_duplicate(self):
        """Test creating a user with a duplicate username."""

        user = await User.create(name="dupeuser", password="password123")

        with pytest.raises(AlreadyExistsException):
            await User.create(name="dupeuser", password="password123")

        await user.delete()

    @pytest.mark.integration
    async def test_create_user_invalid_username(self):
        """Test creating a user with an invalid username."""

        with pytest.raises(InvalidUsernameException):
            await User.create(name="invalid@user", password="password123")

    @pytest.mark.integration
    async def test_create_user_invalid_password(self):
        """Test creating a user with an invalid password."""

        with pytest.raises(InvalidPasswordException):
            await User.create(name="validuser2", password="short")

    @pytest.mark.integration
    async def test_get_by_name(self):
        """Test retrieving a user by name."""

        await User.create(name="findme", password="password123")
        user = await User.get_by_name("findme")

        assert user is not None
        assert user.name == "findme"

        await user.delete()

    @pytest.mark.integration
    async def test_check_password(self):
        """Test checking the password for a user."""

        user = await User.create(name="pwtest", password="password123")

        assert await user.check_password("password123") is True
        assert await user.check_password("wrongpass") is False

        await user.delete()

    @pytest.mark.integration
    async def test_user_creation_creates_docker_network(self):
        """Test that creating a user also creates a Docker network with the user's name."""

        username = "dockernetuser"
        password = "password123"
        client = get_docker_client()

        try:
            net = client.networks.get(username)
            net.remove()
        except docker.errors.NotFound:
            pass

        user = await User.create(name=username, password=password)

        network = client.networks.get(username)
        assert network is not None
        assert network.name == username

        await user.delete()
