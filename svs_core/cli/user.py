import sys

import typer

from rich import print
from rich.table import Table

from svs_core.cli.lib import (
    get_or_exit,
    user_group_name_autocomplete,
    username_autocomplete,
)
from svs_core.cli.state import (
    get_current_username,
    reject_if_not_admin,
)
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException, User
from svs_core.users.user_group import UserGroup

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
    name: str = typer.Argument(
        ...,
        help="Username of the user to retrieve",
        autocompletion=username_autocomplete,
    ),
) -> None:
    """Get a user by name."""

    user = get_or_exit(User, name=name)

    print(user.pprint())


@app.command("list")
def list_users(
    inline: bool = typer.Option(
        False, "-i", "--inline", help="Display users in inline format"
    ),
    group: str = typer.Option(
        None,
        "--group",
        "-g",
        help="Filter users by group name",
        autocompletion=user_group_name_autocomplete,
    ),
) -> None:
    """List all users."""

    if group:
        user_group = get_or_exit(UserGroup, name=group)
        users = user_group.proxy_members
    else:
        users = User.objects.all()

    if len(users) == 0:
        print("No users found.")
        raise typer.Exit(code=0)

    if inline:
        print("\n".join(f"{u}" for u in users))
        raise typer.Exit(code=0)

    table = Table("ID", "Name", "Is Admin", "Groups")
    for user in users:
        table.add_row(
            str(user.id),
            user.name,
            "Yes" if user.is_admin() else "No",
            ", ".join(g.name for g in user.groups.all()) or "/None/",
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


@app.command("delete")
def delete(
    name: str = typer.Argument(
        ...,
        help="Username of the user to delete",
        autocompletion=username_autocomplete,
    ),
) -> None:
    """Delete a user."""

    reject_if_not_admin()

    user = get_or_exit(User, name=name)

    try:
        user.delete()
        print(f"User '{user.name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting user: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command("create-group")
def create_group(
    name: str = typer.Argument(..., help="Name of the new user group"),
    description: str = typer.Option(
        None, "--description", "-d", help="Description of the user group"
    ),
) -> None:
    """Create a new user group."""

    reject_if_not_admin()

    from svs_core.users.user_group import UserGroup

    try:
        user_group = UserGroup.create(name, description)
        print(f"User group '{user_group.name}' created successfully.")
    except AlreadyExistsException as e:
        print(f"Error creating user group: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command("delete-group")
def delete_group(
    name: str = typer.Argument(
        ...,
        help="Name of the user group to delete",
        autocompletion=user_group_name_autocomplete,
    ),
) -> None:
    """Delete a user group."""

    reject_if_not_admin()

    from svs_core.users.user_group import UserGroup

    user_group = get_or_exit(UserGroup, name=name)

    try:
        user_group.delete()
        print(f"User group '{user_group.name}' deleted successfully.")
    except Exception as e:
        print(f"Error deleting user group: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


@app.command("add-to-group")
def add_user_to_group(
    username: str = typer.Argument(
        ...,
        help="Username of the user to add to the group",
        autocompletion=username_autocomplete,
    ),
    group_name: str = typer.Argument(
        ..., help="Name of the user group", autocompletion=user_group_name_autocomplete
    ),
) -> None:
    """Add a user to a user group."""

    reject_if_not_admin()

    from svs_core.users.user_group import UserGroup

    user = get_or_exit(User, name=username)
    user_group = get_or_exit(UserGroup, name=group_name)

    user_group.add_member(user)
    print(f"User '{user.name}' added to group '{user_group.name}' successfully.")


@app.command("remove-from-group")
def remove_user_from_group(
    username: str = typer.Argument(
        ...,
        help="Username of the user to remove from the group",
        autocompletion=username_autocomplete,
    ),
    group_name: str = typer.Argument(
        ..., help="Name of the user group", autocompletion=user_group_name_autocomplete
    ),
) -> None:
    """Remove a user from a user group."""

    reject_if_not_admin()

    from svs_core.users.user_group import UserGroup

    user = get_or_exit(User, name=username)
    user_group = get_or_exit(UserGroup, name=group_name)

    user_group.remove_member(user)
    print(f"User '{user.name}' removed from group '{user_group.name}' successfully.")
