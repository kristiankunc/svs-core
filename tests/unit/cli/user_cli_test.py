from unittest.mock import AsyncMock, MagicMock, patch

from typer.testing import CliRunner

from svs_core.cli.user import user_app
from svs_core.shared.exceptions import NotFoundException
from svs_core.users.user import InvalidUsernameException

runner = CliRunner()


class TestUserCli:
    @patch("svs_core.users.user.User.create", new_callable=AsyncMock)
    def test_create_success(self, mock_create):
        """Test creating a user successfully."""

        mock_user = MagicMock()
        mock_user.name = "alice"
        mock_create.return_value = mock_user

        result = runner.invoke(user_app, ["create", "alice", "password"])

        assert result.exit_code == 0
        assert "alice" in result.output
        mock_create.assert_awaited_once_with("alice", "password")

    @patch("svs_core.users.user.User.create", new_callable=AsyncMock)
    def test_create_invalid(self, mock_create):
        """Test creating a user with an invalid username."""

        mock_create.side_effect = InvalidUsernameException("Invalid username")

        result = runner.invoke(user_app, ["create", "bad", "password"])

        assert result.exit_code == 0
        assert "Invalid username" in result.output

    @patch("svs_core.users.user.User.delete", new_callable=AsyncMock)
    def test_delete_success(self, mock_delete):
        """Test deleting a user that exists."""

        result = runner.invoke(user_app, ["delete", "alice"])

        assert result.exit_code == 0
        assert "alice" in result.output
        mock_delete.assert_awaited_once_with("alice")

    @patch("svs_core.users.user.User.delete", new_callable=AsyncMock)
    def test_delete_not_found(self, mock_delete):
        """Test deleting a user that does not exist."""

        mock_delete.side_effect = NotFoundException("User not found")

        result = runner.invoke(user_app, ["delete", "bob"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()

    @patch("svs_core.users.user.User.get_by_name", new_callable=AsyncMock)
    def test_get_found(self, mock_get):
        """Test getting a user that exists."""

        mock_user = MagicMock()
        mock_user.name = "alice"
        mock_get.return_value = mock_user

        result = runner.invoke(user_app, ["get", "alice"])

        assert result.exit_code == 0
        assert "alice" in result.output
        mock_get.assert_awaited_once_with("alice")

    @patch("svs_core.users.user.User.get_by_name", new_callable=AsyncMock)
    def test_get_not_found(self, mock_get):
        """Test getting a user that does not exist."""

        mock_get.return_value = None

        result = runner.invoke(user_app, ["get", "bob"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()

    @patch("svs_core.users.user.User.get_by_name", new_callable=AsyncMock)
    def test_check_password_correct(self, mock_get):
        """Test checking password for a user that exists and password is correct."""

        mock_user = MagicMock()
        mock_user.check_password = AsyncMock(return_value=True)
        mock_get.return_value = mock_user

        result = runner.invoke(user_app, ["check-password", "alice", "password"])

        assert result.exit_code == 0
        assert "correct" in result.output.lower()
        mock_get.assert_awaited_once_with("alice")
        mock_user.check_password.assert_awaited_once_with("password")

    @patch("svs_core.users.user.User.get_by_name", new_callable=AsyncMock)
    def test_check_password_incorrect(self, mock_get):
        """Test checking password for a user that exists but password is incorrect."""

        mock_user = MagicMock()
        mock_user.check_password = AsyncMock(return_value=False)
        mock_get.return_value = mock_user

        result = runner.invoke(user_app, ["check-password", "alice", "wrong"])

        assert result.exit_code == 0
        assert "incorrect" in result.output.lower()
        mock_get.assert_awaited_once_with("alice")
        mock_user.check_password.assert_awaited_once_with("wrong")

    @patch("svs_core.users.user.User.get_by_name", new_callable=AsyncMock)
    def test_check_password_user_not_found(self, mock_get):
        """Test checking password for a user that does not exist."""

        mock_get.return_value = None

        result = runner.invoke(user_app, ["check-password", "bob", "password"])

        assert result.exit_code == 0
        assert "not found" in result.output.lower()
        mock_get.assert_awaited_once_with("bob")

    @patch("svs_core.users.user.User.get_all", new_callable=AsyncMock)
    def test_list_users_some(self, mock_get_all):
        """Test listing users when some users exist."""

        mock_user1 = MagicMock()
        mock_user1.__str__.return_value = "alice"  # type: ignore
        mock_user2 = MagicMock()
        mock_user2.__str__.return_value = "bob"  # type: ignore
        mock_get_all.return_value = [mock_user1, mock_user2]

        result = runner.invoke(user_app, ["list"])

        assert result.exit_code == 0
        assert "alice" in result.output
        assert "bob" in result.output
        mock_get_all.assert_awaited_once()

    @patch("svs_core.users.user.User.get_all", new_callable=AsyncMock)
    def test_list_users_none(self, mock_get_all):
        """Test listing users when no users exist."""

        mock_get_all.return_value = []

        result = runner.invoke(user_app, ["list"])

        assert result.exit_code == 0
        assert "no users" in result.output.lower()
        mock_get_all.assert_awaited_once()
