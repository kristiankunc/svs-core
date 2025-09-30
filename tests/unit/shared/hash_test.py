import pytest

from svs_core.shared.hash import check_password, hash_password


class TestHash:
    @pytest.mark.unit
    def test_hash_password_returns_bytes(self):
        """Test that hash_password returns a bytes object."""
        password = "mysecret"
        hashed = hash_password(password)
        assert isinstance(hashed, bytes)
        assert hashed != password.encode("utf-8")

    @pytest.mark.unit
    def test_check_password_valid(self):
        """Test that check_password returns True for a valid password."""
        password = "anothersecret"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True

    @pytest.mark.unit
    def test_check_password_invalid(self):
        """Test that check_password returns False for an invalid password."""
        password = "password1"
        wrong_password = "password2"
        hashed = hash_password(password)
        assert check_password(wrong_password, hashed) is False

    @pytest.mark.unit
    def test_hash_password_unique_hashes(self):
        """Test that hash_password generates unique hashes for the same
        password."""
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

    @pytest.mark.unit
    def test_check_password_with_non_utf8_bytes(self):
        """Test that check_password works with non-UTF-8 bytes."""
        password = "pässwörd"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True
