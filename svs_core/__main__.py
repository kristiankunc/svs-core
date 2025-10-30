#!/usr/bin/env python3

import getpass
import os
import sys

from typing import Optional

import django
import typer

os.environ["DJANGO_SETTINGS_MODULE"] = "svs_core.db.settings"

from svs_core.cli.state import set_current_user
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.logger import get_logger

django.setup()

if not EnvManager.get_database_url():
    get_logger(__name__).warning(
        "DATABASE_URL environment variable not set. Running detached from database."
    )

from svs_core.cli.service import app as service_app  # noqa: E402
from svs_core.cli.template import app as template_app  # noqa: E402
from svs_core.cli.user import app as user_app  # noqa: E402

app = typer.Typer(help="SVS CLI", pretty_exceptions_enable=False)

app.add_typer(user_app, name="user")
app.add_typer(template_app, name="template")
app.add_typer(service_app, name="service")


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

    is_admin = user.is_admin() if user else False
    if user:
        set_current_user(user.name, is_admin)

    user_type = "admin" if (user and user.is_admin()) else "standard user"
    user_display = user.name if user else username
    logger.debug(f"{user_display} ({user_type}) ran: {' '.join(sys.argv)}")

    app()


if __name__ == "__main__":
    main()
