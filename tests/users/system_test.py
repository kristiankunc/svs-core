import pytest

from svs_core.users.system import SystemUserManager


class TestSystemUserManager:
    """Unit tests for SystemUserManager class."""

    def test_create_user_standard(self, mocker):
        mock_run_command = mocker.patch("svs_core.users.system.run_command")

        SystemUserManager.create_user("testuser", "password123", admin=False)

        # Verify correct commands were called
        assert mock_run_command.call_count == 2
        mock_run_command.assert_any_call(
            "sudo useradd -m testuser", check=True
        )
        mock_run_command.assert_any_call(
            "echo 'testuser:password123' | sudo chpasswd", check=True
        )

    def test_create_user_admin(self, mocker):
        mock_run_command = mocker.patch("svs_core.users.system.run_command")

        SystemUserManager.create_user("adminuser", "adminpass123", admin=True)

        # Verify correct commands were called
        assert mock_run_command.call_count == 3
        mock_run_command.assert_any_call(
            "sudo useradd -m adminuser", check=True
        )
        mock_run_command.assert_any_call(
            "echo 'adminuser:adminpass123' | sudo chpasswd", check=True
        )
        mock_run_command.assert_any_call(
            "sudo usermod -aG svs-admins adminuser", check=True
        )

    def test_delete_user(self, mocker):
        mock_run_command = mocker.patch("svs_core.users.system.run_command")

        SystemUserManager.delete_user("testuser")

        mock_run_command.assert_called_once_with(
            "sudo userdel -r testuser", check=True
        )

    def test_is_user_in_group_true(self, mocker):
        mock_result = mocker.Mock()
        mock_result.returncode = 0
        mock_run_command = mocker.patch(
            "svs_core.users.system.run_command", return_value=mock_result
        )

        result = SystemUserManager.is_user_in_group("testuser", "groupname")

        assert result is True
        mock_run_command.assert_called_once_with(
            "groups testuser | grep -qw groupname", check=False
        )

    def test_is_user_in_group_false(self, mocker):
        mock_result = mocker.Mock()
        mock_result.returncode = 1
        mock_run_command = mocker.patch(
            "svs_core.users.system.run_command", return_value=mock_result
        )

        result = SystemUserManager.is_user_in_group("testuser", "groupname")

        assert result is False
        mock_run_command.assert_called_once_with(
            "groups testuser | grep -qw groupname", check=False
        )

    def test_get_system_username_from_getlogin(self, mocker):
        mocker.patch("os.getlogin", return_value="currentuser")

        username = SystemUserManager.get_system_username()

        assert username == "currentuser"

    def test_get_system_username_from_sudo_user(self, mocker):
        mocker.patch("os.getlogin", side_effect=OSError())
        mocker.patch.dict("os.environ", {"SUDO_USER": "sudouser"})

        username = SystemUserManager.get_system_username()

        assert username == "sudouser"

    def test_get_system_username_from_pwd(self, mocker):
        mock_pwd_entry = mocker.Mock()
        mock_pwd_entry.pw_name = "pwduser"

        mocker.patch("os.getlogin", side_effect=OSError())
        mocker.patch.dict("os.environ", {}, clear=True)
        mocker.patch("pwd.getpwuid", return_value=mock_pwd_entry)

        username = SystemUserManager.get_system_username()

        assert username == "pwduser"

    def test_get_system_username_from_getpass(self, mocker):
        mocker.patch("os.getlogin", side_effect=OSError())
        mocker.patch.dict("os.environ", {}, clear=True)
        mocker.patch("pwd.getpwuid", side_effect=Exception("pwd failed"))
        mocker.patch("getpass.getuser", return_value="gpuser")

        username = SystemUserManager.get_system_username()

        assert username == "gpuser"

    def test_get_system_username_all_fail(self, mocker):
        mocker.patch("os.getlogin", side_effect=OSError())
        mocker.patch.dict("os.environ", {}, clear=True)
        mocker.patch("pwd.getpwuid", side_effect=Exception("pwd failed"))
        mocker.patch("getpass.getuser",
                     side_effect=Exception("getpass failed"))

        with pytest.raises(RuntimeError):
            SystemUserManager.get_system_username()
