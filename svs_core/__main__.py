#!/usr/bin/env python3

import os
import sys

from importlib.metadata import version
from typing import Optional, cast

import django
import typer

from rich import print

from svs_core.cli.lib import get_or_exit
from svs_core.cli.state import is_current_user_admin, set_current_user, set_verbose_mode
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.logger import add_verbose_handler, get_logger

# Early verbose mode detection before heavy imports trigger logging
if "-v" in sys.argv or "--verbose" in sys.argv:
    set_verbose_mode(True)
    add_verbose_handler()

os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"

if EnvManager.get_runtime_environment() != EnvManager.RuntimeEnvironment.TESTING:
    EnvManager.load_env_file()

django.setup()

if not EnvManager.get_database_url():
    get_logger(__name__).warning(
        "DATABASE_URL environment variable not set. Running detached from database."
    )

from svs_core.cli.service import app as service_app  # noqa: E402
from svs_core.cli.template import app as template_app  # noqa: E402
from svs_core.cli.user import app as user_app  # noqa: E402
from svs_core.cli.utils import app as utils_app  # noqa: E402


def cli_first_user_setup(
    username: Optional[str] = None, password: Optional[str] = None
) -> None:
    """Function prompting user to create in-place, used by the setup script."""
    from svs_core.users.user import User

    if username and password:
        try:
            User.create(username, password, True)
            return
        except Exception as e:
            print(f"{e}\nFailed to create user with provided credentials.")

    else:
        try:
            User.create(
                input("Type your SVS username: ").strip(),
                input("Type your SVS password: ").strip(),
                True,
            )
            return
        except Exception as e:
            print(f"{e}\nFailed to create user, try again")
            return cli_first_user_setup()


def version_callback(value: bool) -> None:
    """Prints the SVS version and exits."""
    if value:
        print(f"SVS version: {version('svs-core')}")
        raise typer.Exit()


app = typer.Typer(help="SVS CLI", pretty_exceptions_enable=False)


@app.callback()
def global_options(
    version_flag: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
    user_override: str | None = typer.Option(
        None, "--user", "-u", help="Override acting user by username (admin only)"
    ),
) -> None:
    """Global options for SVS CLI."""
    if verbose:
        set_verbose_mode(True)
        add_verbose_handler()
        get_logger(__name__).debug("Verbose mode enabled")

    if user_override:
        if not is_current_user_admin():
            print("User overriding is admin only", file=sys.stderr)
            raise typer.Exit(1)

        from svs_core.users.user import User  # noqa: E402

        user_to_override = get_or_exit(User, name=user_override)

        set_current_user(user_to_override.name, True)


app.add_typer(user_app, name="user")
app.add_typer(template_app, name="template")
app.add_typer(service_app, name="service")
app.add_typer(utils_app, name="utils")


def main() -> None:  # noqa: D103
    from svs_core.users.system import SystemUserManager  # noqa: E402
    from svs_core.users.user import User  # noqa: E402

    logger = get_logger(__name__)
    username = SystemUserManager.get_system_username()
    user = User.objects.filter(name=username).first()

    if not user:
        logger.warning(f"User '{username}' tried to run CLI but was not found.")
        print(
            f"You are running as system user '{username}', but no matching SVS user was found."
        )

        sys.exit(1)

    is_admin = cast(User, user).is_admin() if user else False
    if user:
        set_current_user(user.name, is_admin)

    user_type = "admin" if (user and cast(User, user).is_admin()) else "standard user"
    user_display = user.name if user else username
    logger.debug(f"{user_display} ({user_type}) ran: {' '.join(sys.argv)}")

    app()


if __name__ == "__main__":
    main()
