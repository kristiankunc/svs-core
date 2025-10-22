#!/usr/bin/env python3

import getpass
import sys

import django
import typer

from svs_core.cli.state import CURRENT_USERNAME, IS_ADMIN
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.logger import get_logger

django.setup()

# TODO: Figure out a better way to handle initial configurations
if not EnvManager.get_database_url():
    get_logger(__name__).warning(
        "DATABASE_URL environment variable not set. Running detached from database."
    )

from svs_core.cli.service import app as service_app  # noqa: E402
from svs_core.cli.setup import app as setup_app  # noqa: E402
from svs_core.cli.template import app as template_app  # noqa: E402
from svs_core.cli.user import app as user_app  # noqa: E402

app = typer.Typer(help="SVS CLI", pretty_exceptions_enable=False)

app.add_typer(user_app, name="user")
app.add_typer(setup_app, name="setup")
app.add_typer(template_app, name="template")
app.add_typer(service_app, name="service")


def main() -> None:  # noqa: D103
    from svs_core.users.system import SystemUserManager  # noqa: E402
    from svs_core.users.user import User  # noqa: E402

    username = getpass.getuser()
    user = User.objects.filter(name=username).first()

    if not user and sys.argv[1] != "setup":
        print(
            f"You are running as system user '{username}', but no matching SVS user was found."
        )
        get_logger(__name__).warning(
            f"User '{username}' tried to run CLI but was not found."
        )

        if SystemUserManager.is_user_in_group(username, "svs-admins"):
            print(
                "You appear to be an admin user without an SVS user account. Please create your SVS user via: svs user create"
            )
        else:
            sys.exit(1)

    if user and user.is_admin():
        global IS_ADMIN
        IS_ADMIN = True

    if user:
        global CURRENT_USERNAME
        CURRENT_USERNAME = user.name

    get_logger(__name__).debug(
        f"{user if user is not None else username} ({('admin' if IS_ADMIN else 'standard user')}) ran: {' '.join(sys.argv)}"
    )
    app()


if __name__ == "__main__":
    main()
