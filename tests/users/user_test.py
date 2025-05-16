import pytest

from svs_core.users.manager import UserManager

def test_create_user():
    user_manager = UserManager()    
    
    valid_username = "valid_user123"
    user_manager.create_user(valid_username)
    assert user_manager._user_exists(valid_username) == True

    user_manager.delete_user(valid_username)

def test_create_invalid_user():
    user_manager = UserManager()
    
    invalid_username = "invalid user!"
    with pytest.raises(ValueError, match="Invalid username: invalid user!"):
        user_manager.create_user(invalid_username)

    assert user_manager._user_exists(invalid_username) == False

def test_delete_user():
    user_manager = UserManager()

    username_to_delete = "user_to_delete"
    user_manager.create_user(username_to_delete)
    user_manager.delete_user(username_to_delete)

    assert user_manager._user_exists(username_to_delete) == False

def test_delete_nonexistent_user():
    user_manager = UserManager()

    nonexistent_username = "nonexistent_user"
    with pytest.raises(ValueError, match="User nonexistent_user does not exist."):
        user_manager.delete_user(nonexistent_username)

    assert user_manager._user_exists(nonexistent_username) == False
