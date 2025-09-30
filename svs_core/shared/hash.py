import bcrypt


def hash_password(password: str) -> bytes:
    """Hash a password using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        bytes: The hashed password in bytes.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def check_password(password: str, hashed: bytes) -> bool:
    """Check a password against a hashed password.

    Args:
        password (str): The password to check.
        hashed (bytes): The hashed password to check against.

    Returns:
        bool: True if the password matches the hash, False otherwise.
    """
    return bcrypt.checkpw(bytes(password, "utf-8"), hashed)
