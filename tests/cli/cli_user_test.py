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
            ["user", "create", "new_user"],
            input="password123\npassword123\n",
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_create_user_with_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.return_value.name = "new_user"

        result = self.runner.invoke(
            app,
            ["user", "create", "new_user"],
            input="password123\npassword123\n",
        )

        assert mock_admin_check.called
        assert result.exit_code == 0
        assert "User 'new_user' created successfully." in result.output

    def test_create_user_invalid_username(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = InvalidUsernameException("Username is invalid")

        result = self.runner.invoke(
            app,
            ["user", "create", "invalid"],
            input="password123\npassword123\n",
        )

        assert result.exit_code == 1
        assert "Error creating user" in result.output

    def test_create_user_invalid_password(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = InvalidPasswordException()

        result = self.runner.invoke(
            app,
            ["user", "create", "new_user"],
            input="weak\nweak\n",
        )

        assert result.exit_code == 1
        assert "Error creating user" in result.output

    def test_create_user_already_exists(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = AlreadyExistsException("user", "existing_user")

        result = self.runner.invoke(
            app,
            ["user", "create", "existing_user"],
            input="password123\npassword123\n",
        )

        assert result.exit_code == 1
        assert "Error creating user" in result.output

    # Get command tests
    def test_get_existing_user(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.pprint.return_value = "User(name='existing_user')"
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "get", "existing_user"],
        )

        assert result.exit_code == 0
        assert "User(name='existing_user')" in result.output

    def test_get_non_existing_user(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            ["user", "get", "non_existing_user"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_list_users_with_multiple_users(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.users.user.User.objects.all")
        mock_user1 = mocker.MagicMock()
        mock_user1.id = 1
        mock_user1.name = "user1"
        mock_user1.is_admin.return_value = True
        mock_user2 = mocker.MagicMock()
        mock_user2.id = 2
        mock_user2.name = "user2"
        mock_user2.is_admin.return_value = False
        mock_all.return_value = [mock_user1, mock_user2]

        result = self.runner.invoke(
            app,
            ["user", "list"],
        )

        assert result.exit_code == 0
        # Table output should contain user names
        assert "user1" in result.output
        assert "user2" in result.output

    def test_list_users_empty(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.users.user.User.objects.all")
        mock_all.return_value = []

        result = self.runner.invoke(
            app,
            ["user", "list"],
        )

        assert result.exit_code == 0
        assert "No users found." in result.output

    def test_list_users_inline(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.users.user.User.objects.all")
        mock_user1 = mocker.MagicMock()
        mock_user1.__str__.return_value = "User(name='user1')"
        mock_user2 = mocker.MagicMock()
        mock_user2.__str__.return_value = "User(name='user2')"
        mock_all.return_value = [mock_user1, mock_user2]

        result = self.runner.invoke(
            app,
            ["user", "list", "--inline"],
        )

        assert result.exit_code == 0
        assert "User(name='user1')" in result.output
        assert "User(name='user2')" in result.output

    # Add SSH key command tests
    def test_add_ssh_key_user_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="non_existing_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_add_ssh_key_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.get_current_username", return_value="testuser")
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
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "SSH key added to user 'testuser'." in result.output
        mock_user.add_ssh_key.assert_called_once_with(
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"
        )

    # Remove SSH key command tests
    def test_remove_ssh_key_user_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="non_existing_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_remove_ssh_key_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.get_current_username", return_value="testuser")
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
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "SSH key removed from user 'testuser'." in result.output
        mock_user.remove_ssh_key.assert_called_once_with(
            "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"
        )

    def test_add_ssh_key_displays_user_name_from_db(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add-ssh-key displays the user's name from DB."""
        mocker.patch(
            "svs_core.cli.user.get_current_username",
            return_value="current_user_from_context",
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "actual_name_from_db"  # Name from DB
        mock_user.add_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "SSH key added to user 'actual_name_from_db'." in result.output

    def test_remove_ssh_key_displays_user_name_from_db(
        self, mocker: MockerFixture
    ) -> None:
        """Test that remove-ssh-key displays the user's name from DB."""
        mocker.patch(
            "svs_core.cli.user.get_current_username",
            return_value="current_user_from_context",
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "actual_name_from_db"  # Name from DB
        mock_user.remove_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        assert result.exit_code == 0
        assert "SSH key removed from user 'actual_name_from_db'." in result.output

    def test_add_ssh_key_calls_get_with_current_username(
        self, mocker: MockerFixture
    ) -> None:
        """Test that add-ssh-key passes the current username from context to
        User.objects.get."""
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "current_user"
        mock_user.add_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            [
                "user",
                "add-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        mock_get.assert_called_once_with(name="current_user")

    def test_remove_ssh_key_calls_get_with_current_username(
        self, mocker: MockerFixture
    ) -> None:
        """Test that remove-ssh-key passes the current username from context to
        User.objects.get."""
        mocker.patch(
            "svs_core.cli.user.get_current_username", return_value="current_user"
        )
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "current_user"
        mock_user.remove_ssh_key = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            [
                "user",
                "remove-ssh-key",
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        mock_get.assert_called_once_with(name="current_user")

    def test_add_ssh_key_error_handling_on_method_call(
        self, mocker: MockerFixture
    ) -> None:
        """Test that exceptions from add_ssh_key method are not caught by the
        CLI."""
        mocker.patch("svs_core.cli.user.get_current_username", return_value="testuser")
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
        mocker.patch("svs_core.cli.user.get_current_username", return_value="testuser")
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
                "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz",
            ],
        )

        # Exception should propagate and cause non-zero exit
        assert result.exit_code != 0

    # Delete command tests
    def test_delete_user_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "delete", "someuser"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_delete_user_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "deleted_user"
        mock_user.delete = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "delete", "deleted_user"],
        )

        assert result.exit_code == 0
        assert "User 'deleted_user' deleted successfully." in result.output
        mock_user.delete.assert_called_once()

    def test_delete_user_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            ["user", "delete", "non_existing_user"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_delete_user_error_handling_on_method_call(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.delete = mocker.MagicMock(side_effect=Exception("Delete failed"))
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "delete", "testuser"],
        )

        assert result.exit_code == 1
        assert "Error deleting user" in result.output

    def test_delete_calls_get_with_name(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "someuser"
        mock_user.delete = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            ["user", "delete", "someuser"],
        )

        mock_get.assert_called_once_with(name="someuser")

    # Group-related command tests
    def test_create_group_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "create-group", "newgroup"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_create_group_with_admin_rights(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user_group.UserGroup.create")
        mock_create.return_value.name = "newgroup"

        result = self.runner.invoke(
            app,
            ["user", "create-group", "newgroup"],
        )

        assert result.exit_code == 0
        assert "User group 'newgroup' created successfully." in result.output

    def test_delete_group_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "delete-group", "somegroup"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_delete_group_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user_group.UserGroup.objects.get")
        mock_group = mocker.MagicMock()
        mock_group.name = "deleted_group"
        mock_group.delete = mocker.MagicMock()
        mock_get.return_value = mock_group

        result = self.runner.invoke(
            app,
            ["user", "delete-group", "deleted_group"],
        )

        assert result.exit_code == 0
        assert "User group 'deleted_group' deleted successfully." in result.output
        mock_group.delete.assert_called_once()

    def test_add_user_to_group_without_admin_rights(
        self, mocker: MockerFixture
    ) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "add-to-group", "someuser", "group1"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_add_user_to_group_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get_user = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "theuser"
        mock_get_user.return_value = mock_user

        mock_get_group = mocker.patch("svs_core.users.user_group.UserGroup.objects.get")
        mock_group = mocker.MagicMock()
        mock_group.name = "thegroup"
        mock_group.add_member = mocker.MagicMock()
        mock_get_group.return_value = mock_group

        result = self.runner.invoke(
            app,
            ["user", "add-to-group", "theuser", "thegroup"],
        )

        assert result.exit_code == 0
        assert "User 'theuser' added to group 'thegroup' successfully." in result.output
        mock_group.add_member.assert_called_once_with(mock_user)

    def test_remove_user_from_group_without_admin_rights(
        self, mocker: MockerFixture
    ) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "remove-from-group", "someuser", "group1"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_remove_user_from_group_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get_user = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "theuser"
        mock_get_user.return_value = mock_user

        mock_get_group = mocker.patch("svs_core.users.user_group.UserGroup.objects.get")
        mock_group = mocker.MagicMock()
        mock_group.name = "thegroup"
        mock_group.remove_member = mocker.MagicMock()
        mock_get_group.return_value = mock_group

        result = self.runner.invoke(
            app,
            ["user", "remove-from-group", "theuser", "thegroup"],
        )

        assert result.exit_code == 0
        assert (
            "User 'theuser' removed from group 'thegroup' successfully."
            in result.output
        )
        mock_group.remove_member.assert_called_once_with(mock_user)

    # Reset password command tests
    def test_reset_password_without_admin_rights(self, mocker: MockerFixture) -> None:
        mock_admin_check = mocker.patch(
            "svs_core.cli.user.reject_if_not_admin", side_effect=SystemExit(1)
        )

        result = self.runner.invoke(
            app,
            ["user", "reset-password", "someuser"],
        )

        assert mock_admin_check.called
        assert result.exit_code == 1

    def test_reset_password_user_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            ["user", "reset-password", "non_existing_user"],
            input="newpassword\nnewpassword\n",
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_reset_password_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.change_password = mocker.MagicMock()
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "reset-password", "testuser"],
            input="newpassword123\nnewpassword123\n",
        )

        assert result.exit_code == 0
        assert "Password for user 'testuser' reset successfully." in result.output
        mock_user.change_password.assert_called_once_with("newpassword123")

    def test_reset_password_invalid_password(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_user.change_password = mocker.MagicMock(
            side_effect=InvalidPasswordException()
        )
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "reset-password", "testuser"],
            input="weak\nweak\n",
        )

        assert result.exit_code == 1
        assert "Error resetting password" in result.output

    def test_reset_password_mismatch_confirmation(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "testuser"
        mock_get.return_value = mock_user

        result = self.runner.invoke(
            app,
            ["user", "reset-password", "testuser"],
            input="newpassword123\ndifferentpassword\n",
        )

        assert result.exit_code == 1
        assert "Error: The two entered values do not match." in result.output
        mock_user.change_password.assert_not_called()

    def test_reset_password_calls_get_with_username(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user = mocker.MagicMock()
        mock_user.name = "specificuser"
        mock_user.change_password = mocker.MagicMock()
        mock_get.return_value = mock_user

        self.runner.invoke(
            app,
            ["user", "reset-password", "specificuser"],
            input="newpassword123\nnewpassword123\n",
        )

        mock_get.assert_called_once_with(name="specificuser")

    def test_list_users_with_group_filter(self, mocker: MockerFixture) -> None:
        # Patch UserGroup.objects.get and its proxy_members
        mock_get_group = mocker.patch("svs_core.users.user_group.UserGroup.objects.get")
        mock_group = mocker.MagicMock()
        mock_user1 = mocker.MagicMock()
        mock_user1.id = 1
        mock_user1.name = "guser1"
        mock_user1.is_admin.return_value = False
        mock_group.proxy_members = [mock_user1]
        mock_get_group.return_value = mock_group

        result = self.runner.invoke(
            app,
            ["user", "list", "--group", "somegroup"],
        )

        assert result.exit_code == 0
        assert "guser1" in result.output


@pytest.mark.cli
class TestUserPasswordFeatures:
    """Test password prompting and validation in CLI."""

    runner: CliRunner

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_create_user_with_password_prompt_success(
        self, mocker: MockerFixture
    ) -> None:
        """Test user creation with password prompt (happy path)."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_user = mocker.MagicMock()
        mock_user.name = "newuser"
        mock_create.return_value = mock_user

        # Simulate password input: password + confirmation
        result = self.runner.invoke(
            app,
            ["user", "create", "newuser"],
            input="password123\npassword123\n",
        )

        assert result.exit_code == 0
        assert "User 'newuser' created successfully." in result.output
        mock_create.assert_called_once_with("newuser", "password123")

    def test_create_user_with_password_prompt_mismatch(
        self, mocker: MockerFixture
    ) -> None:
        """Test user creation when password confirmation doesn't match."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")

        # Simulate mismatched passwords
        result = self.runner.invoke(
            app,
            ["user", "create", "newuser"],
            input="password123\nwrongpassword\n",
        )

        # typer.prompt with confirmation_prompt=True will show error and abort
        assert result.exit_code == 1
        assert "Error: The two entered values do not match." in result.output
        mock_create.assert_not_called()

    def test_create_user_with_invalid_password_via_prompt(
        self, mocker: MockerFixture
    ) -> None:
        """Test user creation with invalid password (too short) via prompt."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_create.side_effect = InvalidPasswordException()

        result = self.runner.invoke(
            app,
            ["user", "create", "newuser"],
            input="short\nshort\n",
        )

        assert result.exit_code == 1
        assert "Error creating user" in result.output
        assert "Invalid password" in result.output

    def test_create_user_with_special_characters_in_password(
        self, mocker: MockerFixture
    ) -> None:
        """Test user creation with special characters in password."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_user = mocker.MagicMock()
        mock_user.name = "specialuser"
        mock_create.return_value = mock_user

        special_password = "P@ssw0rd!#$%"
        result = self.runner.invoke(
            app,
            ["user", "create", "specialuser"],
            input=f"{special_password}\n{special_password}\n",
        )

        assert result.exit_code == 0
        assert "User 'specialuser' created successfully." in result.output
        mock_create.assert_called_once_with("specialuser", special_password)

    def test_create_user_with_unicode_password(self, mocker: MockerFixture) -> None:
        """Test user creation with unicode characters in password."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_user = mocker.MagicMock()
        mock_user.name = "unicodeuser"
        mock_create.return_value = mock_user

        unicode_password = "pässwörd123"
        result = self.runner.invoke(
            app,
            ["user", "create", "unicodeuser"],
            input=f"{unicode_password}\n{unicode_password}\n",
        )

        assert result.exit_code == 0
        assert "User 'unicodeuser' created successfully." in result.output
        mock_create.assert_called_once_with("unicodeuser", unicode_password)

    def test_create_user_with_minimum_length_password(
        self, mocker: MockerFixture
    ) -> None:
        """Test user creation with exactly 8 character password (minimum)."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_user = mocker.MagicMock()
        mock_user.name = "minuser"
        mock_create.return_value = mock_user

        min_password = "12345678"  # Exactly 8 characters
        result = self.runner.invoke(
            app,
            ["user", "create", "minuser"],
            input=f"{min_password}\n{min_password}\n",
        )

        assert result.exit_code == 0
        assert "User 'minuser' created successfully." in result.output
        mock_create.assert_called_once_with("minuser", min_password)

    def test_create_user_with_spaces_in_password(self, mocker: MockerFixture) -> None:
        """Test user creation with spaces in password."""
        mocker.patch("svs_core.cli.user.reject_if_not_admin")
        mock_create = mocker.patch("svs_core.users.user.User.create")
        mock_user = mocker.MagicMock()
        mock_user.name = "spaceuser"
        mock_create.return_value = mock_user

        password_with_spaces = "my password 123"
        result = self.runner.invoke(
            app,
            ["user", "create", "spaceuser"],
            input=f"{password_with_spaces}\n{password_with_spaces}\n",
        )

        assert result.exit_code == 0
        assert "User 'spaceuser' created successfully." in result.output
        mock_create.assert_called_once_with("spaceuser", password_with_spaces)
