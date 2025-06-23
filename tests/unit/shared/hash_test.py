import pytest

from svs_core.shared.hash import check_password, hash_password


class TestHash:
    @pytest.mark.unit
    def test_hash_password_returns_bytes(self):
        password = "mysecret"
        hashed = hash_password(password)
        assert isinstance(hashed, bytes)
        assert hashed != password.encode("utf-8")

    @pytest.mark.unit
    def test_check_password_valid(self):
        password = "anothersecret"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True

    @pytest.mark.unit
    def test_check_password_invalid(self):
        password = "password1"
        wrong_password = "password2"
        hashed = hash_password(password)
        assert check_password(wrong_password, hashed) is False

    @pytest.mark.unit
    def test_hash_password_unique_hashes(self):
        password = "samepassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        # bcrypt uses a random salt, so hashes should be different
        assert hash1 != hash2

    @pytest.mark.unit
    def test_check_password_with_non_utf8_bytes(self):
        password = "pässwörd"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True
