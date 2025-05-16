import os
import pytest
from pytest_mock import MockFixture

from svs_core.users.manager import UserManager


def test_create_user() -> None:
    user_manager = UserManager()

    valid_username = "valid_user123"
    user_manager.create_user(valid_username)
    assert user_manager.user_exists(valid_username)

    user_manager.delete_user(valid_username)


def test_create_invalid_user() -> None:
    user_manager = UserManager()

    invalid_username = "invalid user!"
    with pytest.raises(ValueError, match="Invalid username: invalid user!"):
        user_manager.create_user(invalid_username)

    assert user_manager.user_exists(invalid_username) == False


def test_delete_user() -> None:
    user_manager = UserManager()

    username_to_delete = "user_to_delete"
    user_manager.create_user(username_to_delete)
    user_manager.delete_user(username_to_delete)

    assert user_manager.user_exists(username_to_delete) == False


def test_delete_nonexistent_user() -> None:
    user_manager = UserManager()

    nonexistent_username = "nonexistent_user"
    with pytest.raises(ValueError, match="User nonexistent_user does not exist."):
        user_manager.delete_user(nonexistent_username)

    assert user_manager.user_exists(nonexistent_username) == False


def test_add_ssh_key() -> None:
    user_manager = UserManager()

    username = "ssh_user"
    key_name = "test_key"
    ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArandomkey"

    if not user_manager.user_exists(username):
        user_manager.create_user(username)

    try:
        user_manager.add_ssh_key(username, key_name, ssh_key)

        authorized_keys_path = f"/home/{username}/.ssh/authorized_keys"
        assert os.path.exists(authorized_keys_path)

        with open(authorized_keys_path, "r") as f:
            content = f.read()
            assert f"# {key_name}" in content
            assert ssh_key in content
    finally:
        user_manager.delete_user(username)


def test_add_ssh_key_user_does_not_exist(mocker: MockFixture) -> None:
    user_manager = UserManager()

    username = "nonexistent_user"
    key_name = "test_key"
    ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArandomkey"

    mocker.patch.object(user_manager, "user_exists", return_value=False)

    with pytest.raises(ValueError, match=f"User {username} does not exist."):
        user_manager.add_ssh_key(username, key_name, ssh_key)


def test_remove_ssh_key() -> None:
    user_manager = UserManager()

    username = "ssh_user"
    key_name = "test_key"
    ssh_key = "ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEArandomkey"

    if not user_manager.user_exists(username):
        user_manager.create_user(username)

    try:
        user_manager.add_ssh_key(username, key_name, ssh_key)
        user_manager.remove_ssh_key(username, key_name)

        authorized_keys_path = f"/home/{username}/.ssh/authorized_keys"
        assert os.path.exists(authorized_keys_path)

        with open(authorized_keys_path, "r") as f:
            content = f.read()
            assert f"# {key_name}" not in content
            assert ssh_key not in content
    finally:
        user_manager.delete_user(username)


def test_remove_ssh_key_user_does_not_exist(mocker: MockFixture) -> None:
    user_manager = UserManager()

    username = "nonexistent_user"
    key_name = "test_key"

    mocker.patch.object(user_manager, "user_exists", return_value=False)

    with pytest.raises(ValueError, match=f"User {username} does not exist."):
        user_manager.remove_ssh_key(username, key_name)


def test_remove_ssh_key_no_authorized_keys_file(mocker: MockFixture) -> None:
    user_manager = UserManager()

    username = "ssh_user"
    key_name = "test_key"

    mocker.patch.object(user_manager, "user_exists", return_value=True)
    mocker.patch("os.path.exists", return_value=False)

    with pytest.raises(ValueError, match=f"No authorized keys file found for user {username}."):
        user_manager.remove_ssh_key(username, key_name)
