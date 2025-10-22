import sys

from contextvars import ContextVar
from typing import cast

current_user: ContextVar[dict[str, bool | str] | None] = ContextVar(
    "current_user", default=None
)


def set_current_user(username: str, is_admin: bool) -> None:
    """Set the current user and their admin status in the context variable."""

    current_user.set({"username": username, "is_admin": is_admin})


def reject_if_not_admin() -> None:
    """Exit the program if the current user is not an admin."""

    user = current_user.get()
    if user is None or not user.get("is_admin", False):
        print(
            "❌ Administrative privileges are required to run this command.",
            file=sys.stderr,
        )
        sys.exit(1)


def get_current_username() -> str | None:
    """Return the current username."""

    user = current_user.get()
    if user is None:
        return None

    return cast(str, user.get("username"))


def is_current_user_admin() -> bool:
    """Return whether the current user is an admin."""

    user = current_user.get()
    if user is None:
        return False

    return cast(bool, user.get("is_admin", False))
