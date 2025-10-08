import typer

from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import InvalidPasswordException, InvalidUsernameException, User

app = typer.Typer(help="Manage users")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Username of the new user"),
    password: str = typer.Argument(..., help="Password for the new user"),
) -> None:
    """Create a new user."""
    try:
        user = User.create(name, password)
        typer.echo(f"✅ User '{user.name}' created successfully.")
    except (
        InvalidUsernameException,
        InvalidPasswordException,
        AlreadyExistsException,
    ) as e:
        typer.echo(f"❌ {e}", err=True)


@app.command("get")
def get(
    name: str = typer.Argument(..., help="Username of the user to retrieve")
) -> None:
    """Get a user by name."""
    user = User.get_by_name(name)
    if user:
        typer.echo(f"👤 User found: {user.name}")
    else:
        typer.echo("❌ User not found.", err=True)


@app.command("check-password")
def check_password(
    name: str = typer.Argument(..., help="Username of the user"),
    password: str = typer.Argument(
        ..., help="Password to check against the stored hash"
    ),
) -> None:
    """Check if a password matches the stored hash."""
    user = User.get_by_name(name)
    if not user:
        typer.echo("❌ User not found.", err=True)
        return

    if user.check_password(password):
        typer.echo("✅ Password is correct.")
    else:
        typer.echo("❌ Incorrect password.", err=True)


@app.command("list")
def list_users() -> None:
    """List all users."""
    users = User.get_all()
    if not users:
        typer.echo("No users found.", err=True)
        return

    typer.echo(f"👥 Total users: {len(users)}")
    typer.echo("\n".join(f"- {user}" for user in users))
