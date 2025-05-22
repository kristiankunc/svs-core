from typing import Generator
import pytest
import os
import stat

from svs_core.event_adapters.base import SideEffectAdapter
from svs_core.event_adapters.system import SystemAdapter
from svs_core.shared.shell import run_command
from svs_core.users.user import User
from svs_core.shared.logger import get_logger


class TestSystemAdapter:
    @pytest.fixture()
    def system_adapter(self) -> SideEffectAdapter:
        """Fixture to create a SystemAdapter instance for testing."""
        return SystemAdapter()

    @pytest.fixture(scope="function")
    def test_user(
        self, system_adapter: SideEffectAdapter
    ) -> Generator[User, None, None]:
        """Fixture to create and delete a test user for each test."""
        username = "testuser"
        system_adapter._create_user(username)  # type: ignore

        user = User(id=1, name=username, ssh_keys=[], _orm_check=True)
        yield user

        system_adapter._delete_user(user)  # type: ignore

    def test_create_user(self, system_adapter: SideEffectAdapter) -> None:
        """Test the _create_user method of SystemAdapter."""

        username = "testuser"
        system_adapter._create_user(username)  # type: ignore

        assert run_command(f"id -u {username}", check=True) is not None, (
            f"User {username} was not created successfully in the system."
        )

        keyfile = f"/home/{username}/.ssh/authorized_keys"
        file_stat = os.stat(keyfile)

        expected_mode = 0o400
        assert (file_stat.st_mode & 0o777) == expected_mode, (
            f"Expected mode 0o400, got {stat.filemode(file_stat.st_mode)}"
        )

        user = User(
            id=1,
            name=username,
            ssh_keys=[],
            _orm_check=True,
        )

        system_adapter._delete_user(user)  # type: ignore

    def test_delete_user(self, system_adapter: SideEffectAdapter) -> None:
        """Test the _delete_user method of SystemAdapter."""

        username = "testuser"
        system_adapter._create_user(username)  # type: ignore

        user = User(
            id=1,
            name=username,
            ssh_keys=[],
            _orm_check=True,
        )

        system_adapter._delete_user(user)  # type: ignore

        result = run_command(f"id -u {username}", check=False)
        assert result is None or result.stdout == "", (
            f"User {username} was not deleted successfully from the system."
        )
        result = run_command(f"sudo ls /home/{username}", check=False)
        assert result is None or result.stdout == "", (
            f"User {username} home directory was not deleted successfully from the system."
        )

    def test_add_ssh_key(
        self, system_adapter: SideEffectAdapter, test_user: User
    ) -> None:
        """Test the _add_ssh_key method of SystemAdapter."""

        key_name = "testkey"
        key_content = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC3..."

        system_adapter._add_ssh_key(test_user, key_name, key_content)  # type: ignore
        keyfile = f"/home/{test_user.name}/.ssh/authorized_keys"

        result = run_command(f"sudo cat {keyfile}", check=True)
        print(result)
        assert result is not None, "Failed to read the authorized_keys file"
        assert key_content in result.stdout, (
            f"SSH key {key_name} was not added successfully for user {test_user.name}."
        )

        get_logger(print(f"Keyfile: {keyfile}"))

        file_stat_result = run_command(f"sudo stat -c '%a' {keyfile}", check=True)
        assert file_stat_result is not None
        file_mode = file_stat_result.stdout.strip()
        assert file_mode == "400", f"Expected mode 400, got {file_mode}"
