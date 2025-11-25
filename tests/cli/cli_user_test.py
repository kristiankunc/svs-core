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

    # Add SSH key command tests
    def test_add_ssh_key_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_add_ssh_key_user_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.return_value = None

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "non_existing_user",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "❌ User not found." in result.output

    def test_add_ssh_key_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.add_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "✅ SSH key added to user 'testuser'." in result.output
        mock_user.add_ssh_key.assert_called_once_with(
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"
        )

    # Remove SSH key command tests
    def test_remove_ssh_key_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_remove_ssh_key_user_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.return_value = None

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "non_existing_user",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "❌ User not found." in result.output

    def test_remove_ssh_key_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.remove_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "✅ SSH key removed from user 'testuser'." in result.output
        mock_user.remove_ssh_key.assert_called_once_with(
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"
        )

    def test_add_ssh_key_displays_user_name_from_db(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add-ssh-key displays the user's name from DB, not the CLI
        argument."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "actual_name_from_db"  # Different from CLI argument
        mock_user.add_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "cli_argument_name",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "✅ SSH key added to user 'actual_name_from_db'." in result.output

    def test_remove_ssh_key_displays_user_name_from_db(
        self, mocker: MockerFixture
    ) -> None:
        """Test that remove-ssh-key displays the user's name from DB, not the
        CLI argument."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "actual_name_from_db"  # Different from CLI argument
        mock_user.remove_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "cli_argument_name",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "✅ SSH key removed from user 'actual_name_from_db'." in result.output

    def test_add_ssh_key_calls_get_with_cli_argument(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add-ssh-key passes the CLI argument to User.objects.get,
        not the DB name."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "db_name"
        mock_user.add_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "cli_arg",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        mock_get.assert_called_once_with(name="cli_arg")

    def test_remove_ssh_key_calls_get_with_cli_argument(
        self, mocker: MockerFixture
    ) -> None:
        """Test that remove-ssh-key passes the CLI argument to
        User.objects.get, not the DB name."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "db_name"
        mock_user.remove_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "cli_arg",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        mock_get.assert_called_once_with(name="cli_arg")

    def test_add_ssh_key_error_handling_on_method_call(
        self, mocker: MockerFixture
    ) -> None:
        """Test that exceptions from add_ssh_key method are not caught by the
        CLI."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.add_ssh_key = mocker.MagicMock(
            side_effect=Exception("SSH key operation failed")
        )
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        # Exception should propagate and cause non-zero exit
        assert result.exit_code != 0

    def test_remove_ssh_key_error_handling_on_method_call(
        self, mocker: MockerFixture
    ) -> None:
        """Test that exceptions from remove_ssh_key method are not caught by
        the CLI."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.remove_ssh_key = mocker.MagicMock(
            side_effect=Exception("SSH key operation failed")
        )
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "testuser",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        # Exception should propagate and cause non-zero exit
        assert result.exit_code != 0
