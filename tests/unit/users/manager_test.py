from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from svs_core.shared.exceptions import UserAlreadyExistsException, UserNotFoundException
from svs_core.users.manager import UserManager
from svs_core.users.user import User


class TestUserManager:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        "username, expected",
        [
            ("validuser", True),
            ("valid_user", True),
            ("valid-user", True),
            ("user123", True),
            ("u", True),
            ("a" * 32, True),
            ("", False),  # Empty username
            ("a" * 33, False),  # Too long
            ("InvalidUser", False),  # Uppercase
            ("-invalid", False),  # Starts with hyphen
            ("invalid-", False),  # Ends with hyphen
            ("invalid user", False),  # Contains space
            ("invalid!", False),  # Contains special char
        ],
    )
    def test_is_username_valid(self, username: str, expected: bool) -> None:
        """Tests the is_username_valid method."""

        assert UserManager.is_username_valid(username) == expected

    @pytest.mark.unit
    def test_username_exists(self, mocker: MockerFixture) -> None:
        """Tests the username_exists method."""

        def mock_get_user_by_name(username: str) -> User | None:
            if username == "existinguser":
                return User(
                    id=1,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    name="existinguser",
                    _orm_check=True,
                )
            return None

        mocker.patch(
            "svs_core.users.manager.DBClient.get_user_by_name",
            side_effect=mock_get_user_by_name,
        )
        assert UserManager.username_exists("existinguser") is True
        assert UserManager.username_exists("nonexistinguser") is False

    @pytest.mark.unit
    def test_create_user_success(self, mocker: MockerFixture) -> None:
        """Tests successful user creation."""

        mocker.patch(
            "svs_core.users.manager.UserManager.is_username_valid", return_value=True
        )
        mocker.patch(
            "svs_core.users.manager.UserManager.username_exists", return_value=False
        )
        mock_db_create_user = mocker.patch(
            "svs_core.users.manager.DBClient.create_user",
            return_value=User(
                id=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                name="newuser",
                _orm_check=True,
            ),
        )
        mock_docker_create_network = mocker.patch(
            "svs_core.users.manager.DockerNetworkManager.create_network"
        )

        user = UserManager.create_user("newuser")

        assert user.name == "newuser"
        mock_db_create_user.assert_called_once_with("newuser")
        mock_docker_create_network.assert_called_once_with("newuser")

    @pytest.mark.unit
    def test_create_user_invalid_username(self, mocker: MockerFixture) -> None:
        """Tests user creation with an invalid username."""

        mocker.patch(
            "svs_core.users.manager.UserManager.is_username_valid", return_value=False
        )
        with pytest.raises(ValueError, match="Invalid username: invaliduser"):
            UserManager.create_user("invaliduser")

    @pytest.mark.unit
    def test_create_user_already_exists(self, mocker: MockerFixture) -> None:
        """Tests user creation when the user already exists."""

        mocker.patch(
            "svs_core.users.manager.UserManager.is_username_valid", return_value=True
        )
        mocker.patch(
            "svs_core.users.manager.UserManager.username_exists", return_value=True
        )
        with pytest.raises(
            UserAlreadyExistsException, match="User 'existinguser' already exists."
        ):
            UserManager.create_user("existinguser")

    @pytest.mark.unit
    def test_get_by_name_success(self, mocker: MockerFixture) -> None:
        """Tests retrieving an existing user by name."""

        expected_user = User(
            id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name="testuser",
            _orm_check=True,
        )
        mocker.patch(
            "svs_core.users.manager.DBClient.get_user_by_name",
            return_value=expected_user,
        )

        user = UserManager.get_by_name("testuser")
        assert user == expected_user

    @pytest.mark.unit
    def test_get_by_name_not_found(self, mocker: MockerFixture) -> None:
        """Tests retrieving a non-existing user by name."""

        mocker.patch(
            "svs_core.users.manager.DBClient.get_user_by_name", return_value=None
        )
        with pytest.raises(
            UserNotFoundException, match="User 'nonexistinguser' not found."
        ):
            UserManager.get_by_name("nonexistinguser")
