import pytest

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException


@pytest.mark.cli
class TestUserCommands:
    runner: CliRunner

    def setup_method(self) -> None:
        self.runner = CliRunner()

    # Create command tests
    def test_create_user_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "create", "new_user", "password123"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_create_user_with_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.return_value.name = "new_user"

        result = self.runner.invoke(
            app,
            ["user", "create", "new_user", "password123"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 0
        assert "✅ User 'new_user' created successfully." in result.output

    def test_create_user_invalid_username(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = InvalidUsernameException("Username is invalid")

        result = self.runner.invoke(
            app,
            ["user", "create", "invalid", "password123"],
        )

        assert result.exit_code == 0
        assert "Invalid username" in result.output

    def test_create_user_invalid_password(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = InvalidPasswordException("Password is too weak")

        result = self.runner.invoke(
            app,
            ["user", "create", "new_user", "weak"],
        )

        assert result.exit_code == 0
        assert "Invalid password" in result.output

    def test_create_user_already_exists(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = AlreadyExistsException("user", "existing_user")

        result = self.runner.invoke(
            app,
            ["user", "create", "existing_user", "password123"],
        )

        assert result.exit_code == 0
        assert "❌" in result.output

    # Get command tests
    def test_get_existing_user(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.__str__.return_value = "User(name='existing_user')"
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "get", "existing_user"],
        )

        assert result.exit_code == 0
        assert "👤 User: User(name='existing_user')" in result.output

    def test_get_non_existing_user(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.return_value = None

        result = self.runner.invoke(
            app,
            ["user", "get", "non_existing_user"],
        )

        assert result.exit_code == 0
        assert "❌ User not found." in result.output

    # Check-password command tests
    def test_check_password_as_admin_correct_password(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=True)
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.check_password.return_value = True
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "check-password", "some_user", "password123"],
        )

        assert result.exit_code == 0
        assert "✅ Password is correct." in result.output

    def test_check_password_as_admin_incorrect_password(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=True)
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.check_password.return_value = False
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "check-password", "some_user", "wrong_password"],
        )

        assert result.exit_code == 0
        assert "❌ Incorrect password." in result.output

    def test_check_password_admin_user_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=True)
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.return_value = None

        result = self.runner.invoke(
            app,
            ["user", "check-password", "non_existing_user", "password123"],
        )

        assert result.exit_code == 0
        assert "❌ User not found." in result.output

    def test_check_password_as_non_admin_own_user_correct(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.check_password.return_value = True
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "check-password", "current_user", "password123"],
        )

        assert result.exit_code == 0
        assert "✅ Password is correct." in result.output

    def test_check_password_as_non_admin_own_user_incorrect(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.check_password.return_value = False
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "check-password", "current_user", "wrong_password"],
        )

        assert result.exit_code == 0
        assert "❌ Incorrect password." in result.output

    def test_check_password_as_non_admin_other_user(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["user", "check-password", "other_user", "password123"],
        )

        assert result.exit_code == 0
        assert (
            "❌ You do not have permission to check other users' passwords."
            in result.output
        )

    def test_check_password_non_admin_own_user_not_found(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.return_value = None

        result = self.runner.invoke(
            app,
            ["user", "check-password", "current_user", "password123"],
        )

        assert result.exit_code == 0
        assert "❌ User not found." in result.output

    def test_list_users_with_multiple_users(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.users.user.User.objects.all")
        mock_user1 = mocker.MagicMock()
        mock_user1.__str__.return_value = "User(name='user1')"
        mock_user2 = mocker.MagicMock()
        mock_user2.__str__.return_value = "User(name='user2')"
        mock_all.return_value = [mock_user1, mock_user2]

        result = self.runner.invoke(
            app,
            ["user", "list"],
        )

        assert result.exit_code == 0
        assert "👥 Total users: 2" in result.output
        assert "- User(name='user1')" in result.output
        assert "- User(name='user2')" in result.output

    def test_list_users_empty(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.users.user.User.objects.all")
        mock_all.return_value = []

        result = self.runner.invoke(
            app,
            ["user", "list"],
        )

        assert result.exit_code == 0
        assert "No users found." in result.output
