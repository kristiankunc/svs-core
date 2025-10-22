import getpass

import typer

from svs_core.cli.state import reject_if_not_admin
from svs_core.shared.env_manager import EnvManager
from svs_core.shared.shell import run_command

app = typer.Typer(help="Setup SVS")

automated_yes = False


def confirm():
    """Prompt user for confirmation to proceed."""
    if automated_yes:
        return

    answer = typer.prompt("Are you sure you want to proceed? (y/n)")
    if answer.lower() != "y":
        raise typer.Abort()


def verify_prerequisites():
    """Verify system prerequisites."""
    # Debian check

    try:
        run_command("ls -f /etc/debian_version", check=True)
        typer.echo("✅ System is Debian-based.")
    except Exception:
        typer.echo(
            "❌ This setup script is designed for Debian-based systems.", err=True
        )
        confirm()

    # docker check
    try:
        run_command("docker --version", check=True)
        typer.echo("✅ Docker is installed.")
    except Exception:
        typer.echo("❌ Docker is not installed or not in PATH.", err=True)
        confirm()

    try:
        result = run_command(
            "docker ps --filter 'name=svs-db' --filter 'name=caddy' --format '{{.Names}}'"
        )
        if "svs-db" in result.stdout and "caddy" in result.stdout:
            typer.echo("✅ Required Docker containers are running.")
        else:
            typer.echo(
                "❌ Required Docker containers 'svs-db' and 'caddy' are not running.",
                err=True,
            )
            confirm()
    except Exception:
        typer.echo(
            "❌ Failed to check Docker containers status.",
            err=True,
        )
        confirm()


def permissions_setup():
    """Set up necessary permissions."""
    # create svs-admins group
    try:
        run_command("getent group svs-admins || sudo groupadd svs-admins", check=True)
        typer.echo("✅ Group 'svs-admins' exists or created.")
    except Exception:
        typer.echo("❌ Failed to create or verify 'svs-admins' group.", err=True)
        raise typer.Abort()

    try:
        username = getpass.getuser()
        run_command(f"sudo usermod -a -G svs-admins {username}", check=True)
        typer.echo(f"✅ User '{username}' added to 'svs-admins' group.")
    except Exception:
        typer.echo("❌ Failed to add user to 'svs-admins' group.", err=True)
        raise typer.Abort()


def create_svs_user():
    """Create svs system user."""
    try:
        run_command("id -u svs", check=True)
        typer.echo("✅ System user 'svs' already exists.")
    except Exception:
        try:
            run_command(
                "sudo useradd --system --no-create-home --shell /usr/sbin/nologin svs",
                check=True,
            )
            typer.echo("✅ System user 'svs' created.")
        except Exception:
            typer.echo("❌ Failed to create system user 'svs'.", err=True)
            raise typer.Abort()


def env_setup():
    """Set up /etc/svs/.env file."""
    env_path = EnvManager.ENV_FILE_PATH
    try:
        run_command(f"test -f {env_path}", check=True)
        typer.echo("✅ /etc/svs/.env already exists.")
        run_command(f"sudo chown svs:svs-admins {env_path}", check=True)
        run_command(f"sudo chmod 640 {env_path}", check=True)
        typer.echo(
            "✅ /etc/svs/.env ownership ensured (svs:svs-admins) and group read access set."
        )
    except Exception:
        try:
            run_command("sudo mkdir -p /etc/svs", check=True)
            run_command("sudo chown -R root:svs-admins /etc/svs", check=True)
            run_command("sudo chmod 2775 /etc/svs", check=True)
            run_command(f"sudo touch {env_path}", check=True)
            # make the file readable by the svs-admins group but writable only by owner
            run_command(f"sudo chmod 640 {env_path}", check=True)
            # make the svs user the owner and svs-admins the group owner
            run_command(f"sudo chown svs:svs-admins {env_path}", check=True)
            typer.echo(
                "✅ /etc/svs/.env created and permissions set. Owner is 'svs' and group 'svs-admins' has read access."
            )
        except Exception:
            typer.echo(
                "❌ Failed to create or set permissions for /etc/svs/.env.", err=True
            )
            raise typer.Abort()


def storage_setup():
    """Set up /var/svs storage."""
    print("Setting up /var/svs storage...")
    try:
        run_command("sudo mkdir -p /var/svs", check=True)
        run_command("sudo chown -R root:svs-admins /var/svs", check=True)
        run_command("sudo chmod 2775 /var/svs", check=True)
        typer.echo(
            "✅ /var/svs created and permissions set. Group svs-admins has full access to /var/svs."
        )
    except Exception:
        typer.echo("❌ Failed to create or set permissions for /var/svs.", err=True)
        raise typer.Abort()


def django_migrations():
    """Run Django migrations."""

    try:
        run_command("python3 -m django makemigrations svs_core", check=True)
        typer.echo("✅ Django makemigrations completed.")
    except Exception:
        typer.echo("❌ Failed to run Django makemigrations.", err=True)
        raise typer.Abort()


@app.command("init")
def init(
    yes: bool = typer.Option(False, "--yes", "-y", help="Automatic yes to prompts")
) -> None:
    """Initialize the SVS environment."""

    typer.echo("Initializing SVS environment...")

    reject_if_not_admin()

    global automated_yes
    automated_yes = yes

    verify_prerequisites()
    permissions_setup()
    create_svs_user()
    env_setup()
    storage_setup()
    django_migrations()

    typer.echo("✅ SVS environment initialization complete.")
    typer.echo("Please configure the /etc/svs/.env file before starting SVS services.")
