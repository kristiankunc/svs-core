import sys

IS_ADMIN = False
CURRENT_USERNAME: str | None = None


def reject_if_not_admin() -> None:
    """Exit the program if the current user is not an admin."""

    if not IS_ADMIN:
        print(
            "❌ Administrative privileges are required to run this command.",
            file=sys.stderr,
        )
        sys.exit(1)
