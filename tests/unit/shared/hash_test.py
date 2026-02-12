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

        assert hash1 != hash2

    @pytest.mark.unit
    def test_check_password_with_non_utf8_bytes(self):
        password = "pässwörd"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True

    @pytest.mark.unit
    def test_hash_password_with_empty_string(self):
        """Test that empty password can be hashed (validation happens elsewhere)."""
        password = ""
        hashed = hash_password(password)
        assert isinstance(hashed, bytes)
        assert check_password(password, hashed) is True

    @pytest.mark.unit
    def test_hash_password_with_very_long_password(self):
        """Test hashing a very long password (>72 chars, bcrypt limit)."""
        password = "a" * 100
        # bcrypt raises ValueError for passwords > 72 bytes
        with pytest.raises(ValueError, match="password cannot be longer than 72 bytes"):
            hash_password(password)

    @pytest.mark.unit
    def test_hash_password_with_special_characters(self):
        """Test hashing password with various special characters."""
        passwords = [
            "p@ssw0rd!",
            "test#123$%^",
            "unicode→→→",
            "emoji🔒🔑",
            "spaces in password",
            "tabs\tand\nnewlines",
        ]
        for password in passwords:
            hashed = hash_password(password)
            assert isinstance(hashed, bytes)
            assert check_password(password, hashed) is True

    @pytest.mark.unit
    def test_check_password_case_sensitive(self):
        """Test that password checking is case sensitive."""
        password = "MyPassword123"
        hashed = hash_password(password)
        assert check_password(password, hashed) is True
        assert check_password("mypassword123", hashed) is False
        assert check_password("MYPASSWORD123", hashed) is False

    @pytest.mark.unit
    def test_hash_password_bcrypt_format(self):
        """Test that the hash follows bcrypt format."""
        password = "testpassword"
        hashed = hash_password(password)
        # bcrypt hashes start with $2b$ (or $2a$, $2y$)
        assert hashed.startswith(b"$2b$") or hashed.startswith(b"$2a$")
        # bcrypt hashes are 60 characters long
        assert len(hashed) == 60

    @pytest.mark.unit
    def test_check_password_wrong_length(self):
        """Test password checking with different lengths."""
        password = "password123"
        hashed = hash_password(password)
        assert check_password("password12", hashed) is False
        assert check_password("password1234", hashed) is False

    @pytest.mark.unit
    def test_hash_password_minimum_length_password(self):
        """Test hashing 8 character password (minimum valid)."""
        password = "12345678"
        hashed = hash_password(password)
        assert isinstance(hashed, bytes)
        assert check_password(password, hashed) is True
