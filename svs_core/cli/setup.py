import typer

from svs_core.shared.shell import run_command

app = typer.Typer(help="Setup SVS")


def confirm():
    answer = typer.prompt("Are you sure you want to proceed? (y/n)")
    if answer.lower() != "y":
        raise typer.Abort()


def verify_prerequisites():
    """Verify system prerequisites"""
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
    """Set up necessary permissions"""

    # create svs-users group
    try:
        run_command("getent group svs-users || sudo groupadd svs-users", check=True)
        typer.echo("✅ Group 'svs-users' exists or created.")
    except Exception:
        typer.echo("❌ Failed to create or verify 'svs-users' group.", err=True)
        raise typer.Abort()

    # create svs-admins group
    try:
        run_command("getent group svs-admins || sudo groupadd svs-admins", check=True)
        typer.echo("✅ Group 'svs-admins' exists or created.")
    except Exception:
        typer.echo("❌ Failed to create or verify 'svs-admins' group.", err=True)
        raise typer.Abort()

    # add current user to svs-admins
    try:
        run_command("sudo usermod -aG svs-admins $USER", check=True)
        typer.echo("✅ User added to 'svs-admins' group.")
    except Exception:
        typer.echo("❌ Failed to add user to 'svs-admins' group.", err=True)
        raise typer.Abort()


def env_setup():
    """Set up environment variables"""

    try:
        run_command("test -f /etc/svs/.env", check=True)
        typer.echo("✅ /etc/svs/.env already exists.")

    except Exception:
        try:
            run_command("sudo mkdir -p /etc/svs", check=True)
            run_command("sudo touch /etc/svs/.env", check=True)
            run_command("sudo chown root:svs-admins /etc/svs/.env", check=True)
            run_command("sudo chmod 640 /etc/svs/.env", check=True)
            typer.echo(
                "✅ /etc/svs/.env created and permissions set. Please manually edit it and re-run the command."
            )
        except Exception:
            typer.echo(
                "❌ Failed to create or set permissions for /etc/svs/.env.", err=True
            )
            raise typer.Abort()

    raise typer.Exit()


@app.command("init")
def init() -> None:
    """Initialize the SVS environment"""
    typer.echo("Initializing SVS environment...")

    verify_prerequisites()
    permissions_setup()
    env_setup()
