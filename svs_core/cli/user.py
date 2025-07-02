import asyncio

import typer

from svs_core.shared.exceptions import NotFoundException
from svs_core.users.user import (
    InvalidPasswordException,
    InvalidUsernameException,
    User,
    UsernameAlreadyExistsException,
)

user_app = typer.Typer(help="Manage users")


@user_app.command("create")
def create(name: str, password: str) -> None:
    """Create a new user"""

    async def _create():
        try:
            user = await User.create(name, password)
            typer.echo(f"✅ User '{user.name}' created successfully.")
        except (
            InvalidUsernameException,
            InvalidPasswordException,
            UsernameAlreadyExistsException,
        ) as e:
            typer.echo(f"❌ {e}")

    asyncio.run(_create())


@user_app.command("delete")
def delete(name: str) -> None:
    """Delete a user by name"""

    async def _delete():
        try:
            await User.delete(name)
            typer.echo(f"✅ User '{name}' deleted successfully.")
        except NotFoundException as e:
            typer.echo(f"❌ {e}")

    asyncio.run(_delete())


@user_app.command("get")
def get(name: str) -> None:
    """Get a user by name"""

    async def _get():
        user = await User.get_by_name(name)
        if user:
            typer.echo(f"👤 User found: {user.name}")
        else:
            typer.echo("❌ User not found.")

    asyncio.run(_get())


@user_app.command("check-password")
def check_password(name: str, password: str) -> None:
    """Check if a password matches the stored hash"""

    async def _check():
        user = await User.get_by_name(name)
        if not user:
            typer.echo("❌ User not found.")
            return

        if await user.check_password(password):
            typer.echo("✅ Password is correct.")
        else:
            typer.echo("❌ Incorrect password.")

    asyncio.run(_check())


@user_app.command("list")
def list_users() -> None:
    """List all users"""

    async def _list():
        users = await User.get_all()
        if not users:
            typer.echo("No users found.")
            return

        typer.echo("👥 Users:")
        for user in users:
            typer.echo(f"- {user}")

    asyncio.run(_list())
