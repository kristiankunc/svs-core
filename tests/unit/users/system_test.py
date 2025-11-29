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
        mock_run_command.assert_any_call(
            f"sudo adduser --shell /bin/bash --disabled-password --gecos '' {username}",
            check=True,
        )
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
        mock_run_command.assert_any_call(
            f"sudo adduser --shell /bin/bash --disabled-password --gecos '' {username}",
            check=True,
        )
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
    def test_get_system_username_returns_effective_user(
        self, mocker: MockerFixture
    ) -> None:
        mock_pwd = mocker.MagicMock()
        mock_pwd.pw_name = "effective_user"
        mock_geteuid = mocker.patch(
            "svs_core.users.system.os.geteuid", return_value=1000
        )
        mock_getpwuid = mocker.patch(
            "svs_core.users.system.pwd.getpwuid", return_value=mock_pwd
        )

        username = SystemUserManager.get_system_username()
        mock_geteuid.assert_called_once()
        mock_getpwuid.assert_called_once_with(1000)
        assert username == "effective_user"

    @pytest.mark.unit
    def test_get_system_username_fallback_to_getlogin(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "svs_core.users.system.pwd.getpwuid", side_effect=Exception("No pwd")
        )
        mock_getlogin = mocker.patch(
            "svs_core.users.system.os.getlogin", return_value="login_user"
        )

        username = SystemUserManager.get_system_username()
        mock_getlogin.assert_called_once()
        assert username == "login_user"

    @pytest.mark.unit
    def test_get_system_username_fallback_to_getpass(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "svs_core.users.system.pwd.getpwuid", side_effect=Exception("No pwd")
        )
        mocker.patch(
            "svs_core.users.system.os.getlogin", side_effect=Exception("No login")
        )
        mock_getuser = mocker.patch(
            "svs_core.users.system.getpass.getuser", return_value="getpass_user"
        )

        username = SystemUserManager.get_system_username()
        mock_getuser.assert_called_once()
        assert username == "getpass_user"

    @pytest.mark.unit
    def test_add_ssh_key_to_user(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_pwd_struct = mocker.MagicMock()
        mock_pwd_struct.pw_dir = "/home/testuser"
        mocker.patch("svs_core.users.system.pwd.getpwnam", return_value=mock_pwd_struct)
        mocker.patch("builtins.open", mocker.mock_open())

        username = "testuser"
        ssh_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"

        SystemUserManager.add_ssh_key_to_user(username, ssh_key)

        assert mock_run_command.call_count == 7
        mock_run_command.assert_any_call(
            "sudo mkdir -p /home/testuser/.ssh", check=True
        )
        mock_run_command.assert_any_call(
            "sudo chown testuser:testuser /home/testuser/.ssh", check=True
        )
        mock_run_command.assert_any_call(
            "sudo chmod 700 /home/testuser/.ssh", check=True
        )
        mock_run_command.assert_any_call(
            "sudo bash -c 'cat /tmp/temp_authorized_keys >> /home/testuser/.ssh/authorized_keys'",
            check=True,
        )
        mock_run_command.assert_any_call(
            "sudo chown testuser:testuser /home/testuser/.ssh/authorized_keys",
            check=True,
        )
        mock_run_command.assert_any_call(
            "sudo chmod 600 /home/testuser/.ssh/authorized_keys", check=True
        )
        mock_run_command.assert_any_call(
            "sudo rm /tmp/temp_authorized_keys", check=True
        )

    @pytest.mark.unit
    def test_add_ssh_key_to_user_writes_temp_file(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_pwd_struct = mocker.MagicMock()
        mock_pwd_struct.pw_dir = "/home/testuser"
        mocker.patch("svs_core.users.system.pwd.getpwnam", return_value=mock_pwd_struct)
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        username = "testuser"
        ssh_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"

        SystemUserManager.add_ssh_key_to_user(username, ssh_key)

        mock_open.assert_called_once_with("/tmp/temp_authorized_keys", "w")
        mock_open().write.assert_called_once_with(ssh_key + "\n")

    @pytest.mark.unit
    def test_remove_ssh_key_from_user(self, mocker: MockerFixture) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_pwd_struct = mocker.MagicMock()
        mock_pwd_struct.pw_dir = "/home/testuser"
        mocker.patch("svs_core.users.system.pwd.getpwnam", return_value=mock_pwd_struct)
        mocker.patch("builtins.open", mocker.mock_open())

        username = "testuser"
        ssh_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"

        SystemUserManager.remove_ssh_key_from_user(username, ssh_key)

        assert mock_run_command.call_count == 5
        mock_run_command.assert_any_call(
            "sudo grep -v -f /tmp/temp_key_to_remove /home/testuser/.ssh/authorized_keys > /tmp/temp_authorized_keys_remove",
            check=False,
        )
        mock_run_command.assert_any_call(
            "sudo mv /tmp/temp_authorized_keys_remove /home/testuser/.ssh/authorized_keys",
            check=True,
        )
        mock_run_command.assert_any_call(
            "sudo chown testuser:testuser /home/testuser/.ssh/authorized_keys",
            check=True,
        )
        mock_run_command.assert_any_call(
            "sudo chmod 600 /home/testuser/.ssh/authorized_keys", check=True
        )
        mock_run_command.assert_any_call("sudo rm /tmp/temp_key_to_remove", check=True)

    @pytest.mark.unit
    def test_remove_ssh_key_from_user_writes_temp_file(
        self, mocker: MockerFixture
    ) -> None:
        mock_run_command = mocker.patch("svs_core.users.system.run_command")
        mock_pwd_struct = mocker.MagicMock()
        mock_pwd_struct.pw_dir = "/home/testuser"
        mocker.patch("svs_core.users.system.pwd.getpwnam", return_value=mock_pwd_struct)
        mock_open = mocker.patch("builtins.open", mocker.mock_open())

        username = "testuser"
        ssh_key = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIJVGeX1Zlsp0gRox2uPlaF+/M1Peqtj8kNOMdSLJswfz"

        SystemUserManager.remove_ssh_key_from_user(username, ssh_key)

        mock_open.assert_called_once_with("/tmp/temp_key_to_remove", "w")
        mock_open().write.assert_called_once_with(ssh_key)
