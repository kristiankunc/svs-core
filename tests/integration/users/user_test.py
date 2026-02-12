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


@pytest.mark.integration
class TestUserPasswordSecurity:
    """Integration tests for password security features."""

    @pytest.mark.django_db
    def test_password_is_hashed_on_creation(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that password is hashed and not stored in plaintext."""
        username = "hashtest"
        password = "myplainpassword"
        user = User.create(name=username, password=password)

        # Password should be hashed, not stored in plaintext
        assert user.password != password
        # Hashed password should start with bcrypt identifier
        assert user.password.startswith("$2b$") or user.password.startswith("$2a$")
        # Hashed password should be 60 characters (bcrypt hash length)
        assert len(user.password) == 60

    @pytest.mark.django_db
    def test_password_hash_is_stored_as_string(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that password hash is stored as string in database."""
        username = "stringtest"
        password = "password123"
        user = User.create(name=username, password=password)

        # Retrieve from database
        user_from_db = User.objects.get(name=username)
        assert isinstance(user_from_db.password, str)
        # Verify password still works after retrieval
        assert user_from_db.check_password(password) is True

    @pytest.mark.django_db
    def test_different_users_same_password_different_hashes(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that same password for different users produces different hashes."""
        password = "samepassword"
        user1 = User.create(name="user1", password=password)
        user2 = User.create(name="user2", password=password)

        # Same password should produce different hashes due to salt
        assert user1.password != user2.password
        # Both should validate correctly
        assert user1.check_password(password) is True
        assert user2.check_password(password) is True

    @pytest.mark.django_db
    def test_password_validation_enforced_on_creation(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that password validation is enforced during user creation."""
        username = "validuser3"

        # Test minimum length boundary
        with pytest.raises(InvalidPasswordException):
            User.create(name=username, password="1234567")  # 7 chars, too short

        # 8 chars should work
        user = User.create(name=username, password="12345678")
        assert user is not None

    @pytest.mark.django_db
    def test_check_password_case_sensitive(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that password checking is case sensitive."""
        username = "casetest"
        password = "MyPassword123"
        user = User.create(name=username, password=password)

        assert user.check_password(password) is True
        assert user.check_password("mypassword123") is False
        assert user.check_password("MYPASSWORD123") is False

    @pytest.mark.django_db
    def test_check_password_with_special_characters(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test password checking with special characters."""
        username = "specialtest"
        password = "P@ssw0rd!#$%^&*()"
        user = User.create(name=username, password=password)

        assert user.check_password(password) is True
        assert user.check_password("P@ssw0rd!#$%^&*()X") is False

    @pytest.mark.django_db
    def test_check_password_with_unicode(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test password checking with unicode characters."""
        username = "unicodetest"
        password = "pässwörd123"
        user = User.create(name=username, password=password)

        assert user.check_password(password) is True
        assert user.check_password("password123") is False

    @pytest.mark.django_db
    def test_password_hash_persists_across_retrievals(
        self, mock_docker_network_create, mock_system_user_create
    ):
        """Test that password hash remains consistent across database retrievals."""
        username = "persisttest"
        password = "testpassword"
        user = User.create(name=username, password=password)
        original_hash = user.password

        # Retrieve multiple times
        user1 = User.objects.get(name=username)
        user2 = User.objects.get(name=username)

        # Hash should be identical
        assert user1.password == original_hash
        assert user2.password == original_hash
        # Password should still validate
        assert user1.check_password(password) is True
        assert user2.check_password(password) is True
