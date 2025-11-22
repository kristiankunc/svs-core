import pytest

from pytest_mock import MockerFixture

from svs_core.users.system import SystemUserManager


class TestSystemUser:
    @pytest.mark.unit
    def test_create_normal_user(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        username = "testuser"
        password = "password"

        SystemUserManager.create_user(username, password)

        assert mock_run_command.call_count == 2
        mock_run_command.assert_any_call(f"sudo useradd -m {username}", check=True)
        mock_run_command.assert_any_call(
            f"echo '{username}:{password}' | sudo chpasswd", check=True
        )

    @pytest.mark.unit
    def test_create_admin_user(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        username = "adminuser"
        password = "adminpass"

        SystemUserManager.create_user(username, password, admin=True)

        assert mock_run_command.call_count == 3
        mock_run_command.assert_any_call(f"sudo useradd -m {username}", check=True)
        mock_run_command.assert_any_call(
            f"echo '{username}:{password}' | sudo chpasswd", check=True
        )
        mock_run_command.assert_any_call(
            f"sudo usermod -aG svs-admins {username}", check=True
        )

    @pytest.mark.unit
    def test_delete_user(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        username = "testuser"

        SystemUserManager.delete_user(username)

        mock_run_command.assert_called_once_with(
            f"sudo userdel -r {username}", check=True
        )

    @pytest.mark.unit
    def test_is_user_in_group_user_in_group(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_run_command.return_value.returncode = 0

        username = "testuser"
        groupname = "testgroup"

        result = SystemUserManager.is_user_in_group(username, groupname)

        mock_run_command.assert_called_once_with(
            f"groups {username} | grep -qw {groupname}", check=False
        )
        assert result is True

    @pytest.mark.unit
    def test_is_user_in_group_user_not_in_group(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_run_command.return_value.returncode = 1

        username = "testuser"
        groupname = "testgroup"

        result = SystemUserManager.is_user_in_group(username, groupname)

        mock_run_command.assert_called_once_with(
            f"groups {username} | grep -qw {groupname}", check=False
        )
        assert result is False

    @pytest.mark.unit
    def test_get_system_username_with_sudo(self, mocker: MockerFixture) -> None:
        mock_pwd = mocker.MagicMock()
        mock_pwd.pw_name = "sudo_user"
        mock_getpwuid = mocker.patch(
            "svs_core.users.system.pwd.getpwuid", return_value=mock_pwd
        )

        username = SystemUserManager.get_system_username()
        mock_getpwuid.assert_called_once()
        assert username == "sudo_user"
        assert username == "sudo_user"

    @pytest.mark.unit
    def test_get_system_username_without_sudo(self, mocker: MockerFixture) -> None:
        mock_pwd = mocker.MagicMock()
        mock_pwd.pw_name = "normal_user"
        mock_getpwuid = mocker.patch(
            "svs_core.users.system.pwd.getpwuid", return_value=mock_pwd
        )

        username = SystemUserManager.get_system_username()
        mock_getpwuid.assert_called_once()
        assert username == "normal_user"
