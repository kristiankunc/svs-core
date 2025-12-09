import sys

import typer

from rich import print
from rich.table import Table

from svs_core.cli.lib import get_or_exit
from svs_core.cli.state import (
    get_current_username,
    is_current_user_admin,
    reject_if_not_admin,
)
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException, User

app = typer.Typer(help="Manage users")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Username of the new user"),
    password: str = typer.Argument(..., help="Password for the new user"),
) -> None:
    """Create a new user."""

    reject_if_not_admin()

    try:
        user = User.create(name, password)
        print(f"User '{user.name}' created successfully.")
    except (
        InvalidUsernameException,
        InvalidPasswordException,
        AlreadyExistsException,
    ) as e:
        print(f"Error creating user: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command("get")
def get(
    name: str = typer.Argument(..., help="Username of the user to retrieve")
) -> None:
    """Get a user by name."""

    user = get_or_exit(User, name=name)

    print(user)


@app.command("list")
def list_users(
    inline: bool = typer.Option(
        False, "-i", "--inline", help="Display users in inline format"
    )
) -> None:
    """List all users."""

    users = User.objects.all()
    if len(users) == 0:
        print("No users found.")
        raise typer.Exit(code=0)

    if inline:
        print("\n".join(f"{u}" for u in users))
        raise typer.Exit(code=0)

    table = Table("ID", "Name", "Is Admin")
    for user in users:
        table.add_row(
            str(user.id),
            user.name,
            "Yes" if user.is_admin() else "No",
        )
    print(table)


@app.command("add-ssh-key")
def add_ssh_key(
    ssh_key: str = typer.Argument(..., help="SSH key to add to the user"),
) -> None:
    """Add an SSH key to a user's authorized_keys file."""

    user = get_or_exit(User, name=get_current_username())

    user.add_ssh_key(ssh_key)
    print(f"SSH key added to user '{user.name}'.")


@app.command("remove-ssh-key")
def remove_ssh_key(
    ssh_key: str = typer.Argument(..., help="SSH key to remove from the user"),
) -> None:
    """Remove an SSH key from a user's authorized_keys file."""

    user = get_or_exit(User, name=get_current_username())

    user.remove_ssh_key(ssh_key)
    print(f"SSH key removed from user '{user.name}'.")
