import pytest

from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException, User


class TestUserIntegration:
    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_success(
        self, mock_docker_network_create, mock_system_user_create
    ):
        username = "testuser"
        password = "password123"

        user = User.create(name=username, password=password)

        assert user.name == username
        assert User.objects.get(name=username) is not None
        mock_docker_network_create.assert_called_once_with(
            username,
            labels={"svs_user": username},
        )
        mock_system_user_create.assert_called_once_with(username, password, False)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_duplicate(
        self, mock_docker_network_create, mock_system_user_create
    ):
        username = "dupeuser"
        password = "password123"
        User.create(name=username, password=password)
        with pytest.raises(AlreadyExistsException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_invalid_username(
        self, mock_docker_network_create, mock_system_user_create
    ):
        username = "invalid@user"
        password = "password123"
        with pytest.raises(InvalidUsernameException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_invalid_password(
        self, mock_docker_network_create, mock_system_user_create
    ):
        username = "validuser2"
        password = "short"
        with pytest.raises(InvalidPasswordException):
            User.create(name=username, password=password)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_delete_user_success(
        self,
        mock_docker_network_create,
        mock_docker_network_delete,
        mock_system_user_create,
        mock_system_user_delete,
        mock_volume_delete,
    ):
        username = "deletetest"
        password = "password123"
        user = User.create(name=username, password=password)

        user_id = user.id

        user.delete()

        mock_docker_network_delete.assert_called_once_with(username)
        mock_system_user_delete.assert_called_once_with(username)
        mock_volume_delete.assert_called_once_with(user_id)

        with pytest.raises(User.DoesNotExist):
            User.objects.get(name=username)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_check_password(self, mock_docker_network_create, mock_system_user_create):
        username = "pwtest"
        password = "password123"
        user = User.create(name=username, password=password)

        assert user.check_password(password) is True
        assert user.check_password("wrongpass") is False
