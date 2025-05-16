import subprocess
import pytest
from svs_core.users.manager import UserManager


def sudo_available() -> bool:
    return subprocess.call(
        ['which', 'sudo'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0


pytestmark = pytest.mark.skipif(
    not sudo_available(),
    reason="Tests require root privileges and sudo available in the devcontainer."
)


def test_is_username_valid() -> None:
    manager = UserManager()

    assert manager.is_username_valid("validuser")
    assert manager.is_username_valid("user_123")

    assert not manager.is_username_valid("InvalidUser")
    assert not manager.is_username_valid("user!")
    assert not manager.is_username_valid("")


def test_create_and_delete_user() -> None:
    manager = UserManager()
    username = "testuser_manager"

    if manager.user_exists(username):
        manager.delete_user(username)
    assert not manager.user_exists(username)

    manager.create_user(username)
    assert manager.user_exists(username)

    manager.delete_user(username)
    assert not manager.user_exists(username)


def test_create_user_invalid() -> None:
    manager = UserManager()

    with pytest.raises(ValueError):
        manager.create_user("bad user!")


def test_create_user_already_exists() -> None:
    manager = UserManager()
    username = "testuser_manager2"

    if not manager.user_exists(username):
        manager.create_user(username)

    with pytest.raises(ValueError):
        manager.create_user(username)

    manager.delete_user(username)


def test_delete_user_not_exists() -> None:
    manager = UserManager()
    username = "nouser_manager"

    if manager.user_exists(username):
        manager.delete_user(username)

    with pytest.raises(ValueError):
        manager.delete_user(username)


def test_add_and_remove_ssh_key() -> None:
    manager = UserManager()
    username = "testuser_ssh"
    key_name = "pytest_key"
    ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCtestpytestkey user@host"

    if not manager.user_exists(username):
        manager.create_user(username)

    manager.add_ssh_key(username, key_name, ssh_key)

    result = subprocess.run([
        "sudo", "cat", f"/home/{username}/.ssh/authorized_keys"
    ], capture_output=True, text=True, check=True)

    content = result.stdout

    assert key_name in content and ssh_key in content

    manager.remove_ssh_key(username, key_name)
    result = subprocess.run([
        "sudo", "cat", f"/home/{username}/.ssh/authorized_keys"
    ], capture_output=True, text=True, check=True)
    content = result.stdout

    for line in content.splitlines():
        assert not (key_name in line and ssh_key in line)

    manager.delete_user(username)
