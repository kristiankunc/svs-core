import sys

from contextvars import ContextVar
from typing import cast

import typer

from rich import print

current_user: ContextVar[dict[str, bool | str] | None] = ContextVar(
    "current_user", default=None
)

verbose_mode: ContextVar[bool] = ContextVar("verbose_mode", default=False)


def set_current_user(username: str, is_admin: bool) -> None:
    """Set the current user and their admin status in the context variable."""

    current_user.set({"username": username, "is_admin": is_admin})


def set_verbose_mode(value: bool) -> None:
    """Set the verbose mode in the context variable."""
    verbose_mode.set(value)


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    return verbose_mode.get()


def reject_if_not_admin() -> None:
    """Exit the program if the current user is not an admin."""

    user = current_user.get()
    if user is None or not user.get("is_admin", False):
        print("Admin privileges required.", file=sys.stderr)
        raise typer.Exit(code=1)


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
