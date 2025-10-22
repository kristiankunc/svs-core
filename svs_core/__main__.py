#!/usr/bin/env python3

import getpass
import sys

import django
import typer

from svs_core.cli.state import set_current_user
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

    logger = get_logger(__name__)
    username = getpass.getuser()
    user = User.objects.filter(name=username).first()
    is_setup_command = len(sys.argv) > 1 and sys.argv[1] == "setup"

    if not user and not is_setup_command:
        logger.warning(f"User '{username}' tried to run CLI but was not found.")
        print(
            f"You are running as system user '{username}', but no matching SVS user was found."
        )

        is_admin_user = SystemUserManager.is_user_in_group(username, "svs-admins")
        if is_admin_user:
            print(
                "You appear to be an admin user without an SVS user account. "
                "Please create your SVS user via: svs user create"
            )

            # Auto-create admin for first user
            if not User.objects.exists():
                print(
                    "Since you are the first user, an admin account will be created for you."
                )
                logger.info(
                    f"Granting in-place admin account to system user '{username}'."
                )
                set_current_user(username, True)
        else:
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
