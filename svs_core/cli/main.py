import sys
from typing import cast

from rich import print

from svs_core.cli.app import app
from svs_core.cli.lib import get_or_exit
from svs_core.cli.runtime import setup_runtime
from svs_core.cli.state import (
    is_current_user_admin,
    set_current_user,
    set_verbose_mode,
)
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.logger import add_verbose_handler, get_logger
from svs_core.users.system import SystemUserManager
from svs_core.users.user import User


def _apply_global_options(ctx: dict) -> None:
    if ctx["verbose"]:
        set_verbose_mode(True)
        add_verbose_handler()

    if ctx["user_override"]:
        if not is_current_user_admin():
            print("User overriding is admin only", file=sys.stderr)
            sys.exit(1)

        user = get_or_exit(User, name=ctx["user_override"])
        set_current_user(user.name, user.is_admin())


@app.callback(invoke_without_command=True)
def runtime_callback(
    ctx: typer.Context,
    version: bool,
    verbose: bool,
    user_override: str | None,
) -> None:
    ctx.ensure_object(dict)
    ctx.obj.update(
        version=version,
        verbose=verbose,
        user_override=user_override,
    )


def main() -> None:
    setup_runtime()

    logger = get_logger(__name__)

    username = SystemUserManager.get_system_username()
    user = User.objects.filter(name=username).first()

    if not user:
        print(f"No matching SVS user for system user '{username}'.")
        sys.exit(1)

    if (
        not os.environ.get("SUDO_USER")
        and EnvManager.get_runtime_environment()
        == EnvManager.RuntimeEnvironment.PRODUCTION
    ):
        print("SVS CLI must be run with sudo.")
        sys.exit(1)

    set_current_user(user.name, cast(User, user).is_admin())

    app()
