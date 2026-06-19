"""CLI command for initializing the SVS environment on a server.

Replaces the application-level portion of the old bash install.sh with
an idempotent Python command. Handles Docker Compose setup, Django
migrations, template import, admin user creation, and bash completion
installation.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
import time

from getpass import getpass
from importlib.resources import files as pkg_files
from pathlib import Path
from string import Template as StrTemplate

import docker
import typer

from rich import print

from svs_core.shared.logger import get_logger

logger = get_logger(__name__)

# Styled log prefixes (Rich markup - no emojis)
OK = "[bold green]OK[/bold green]"
INFO = "[bold yellow]INFO[/bold yellow]"
WARN = "[bold yellow]WARN[/bold yellow]"
ERR = "[bold red]ERROR[/bold red]"

DOCKER_COMPOSE_CONTENT = StrTemplate("""\
name: "svs-core"

services:
  db:
    image: postgres:latest
    restart: unless-stopped
    container_name: svs-db
    ports:
      - "5432:5432"
    env_file:
      - stack.env
    volumes:
      - pgdata:/var/lib/postgresql

  caddy:
    image: lucaslorentz/caddy-docker-proxy:latest
    container_name: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - caddy_data:/data
      - caddy_config:/config
    environment:
      - CADDY_INGRESS_NETWORK=caddy
    networks:
      - caddy

volumes:
  pgdata:
  caddy_data:
  caddy_config:

networks:
  caddy:
    name: caddy
    driver: bridge
""")

SVS_CONFIG_DIR = Path("/etc/svs")
SVS_DOCKER_DIR = SVS_CONFIG_DIR / "docker"
STACK_ENV_PATH = SVS_DOCKER_DIR / "stack.env"
COMPOSE_PATH = SVS_DOCKER_DIR / "docker-compose.yml"
SVS_ENV_PATH = SVS_CONFIG_DIR / ".env"


def _verify_docker() -> docker.DockerClient:
    """Check that the Docker daemon is running and accessible.

    Returns:
        A connected Docker client.

    Raises:
        typer.Exit: If Docker is not available.
    """
    try:
        client = docker.from_env()
        client.ping()
        print(f"{OK} Docker daemon is running.")
        return client
    except docker.errors.DockerException:
        print(f"{ERR} Docker daemon is not running or not accessible.", file=sys.stderr)
        print(f"  Please start Docker and try again.", file=sys.stderr)
        raise typer.Exit(code=1)


def _setup_docker_compose(non_interactive: bool) -> str:
    """Create the Docker Compose stack file and credentials.

    Args:
        non_interactive: If True, skip interactive prompts.

    Returns:
        The generated PostgreSQL password for the stack.
    """
    SVS_DOCKER_DIR.mkdir(parents=True, exist_ok=True)

    # Write docker-compose.yml if not present
    if not COMPOSE_PATH.exists():
        COMPOSE_PATH.write_text(DOCKER_COMPOSE_CONTENT.substitute())
        COMPOSE_PATH.chmod(0o660)
        print(f"{OK} Created {COMPOSE_PATH}.")
    else:
        print(f"{OK} {COMPOSE_PATH} already exists.")

    # Read or generate credentials
    #
    # Security note: the password is stored in clear text in the .env file
    # because Docker Compose requires it to pass to the PostgreSQL container.
    # The file is created with 0o660 (owner+group read/write) to mitigate
    # unauthorized access. This is standard practice for Docker Compose
    # deployments and is an accepted risk in this self-hosted context.
    if STACK_ENV_PATH.exists():
        print(f"{OK} {STACK_ENV_PATH} already exists, reusing credentials.")
        password = _read_stack_password()
    else:
        password = secrets.token_hex(16)
        stack_env = (
            f"POSTGRES_USER=svs\n"
            f"POSTGRES_PASSWORD={password}\n"
            f"POSTGRES_DB=svsdb\n"
            f"POSTGRES_HOST=localhost\n"
        )
        STACK_ENV_PATH.write_text(stack_env)
        STACK_ENV_PATH.chmod(0o660)
        print(f"{OK} {STACK_ENV_PATH} created.")

    return password


def _read_stack_password() -> str:
    """Read the PostgreSQL password from the existing stack.env.

    Returns:
        The password string.
    """
    for line in STACK_ENV_PATH.read_text().splitlines():
        if line.startswith("POSTGRES_PASSWORD="):
            return line.split("=", 1)[1]
    # Fallback: generate a new one
    return secrets.token_hex(16)


def _start_stack(password: str) -> None:
    """Start the Docker Compose stack and wait for PostgreSQL readiness.

    Args:
        password: The PostgreSQL password for readiness checks.
    """
    import subprocess

    compose_cmd = [
        "docker",
        "compose",
        "-f",
        str(COMPOSE_PATH),
        "--env-file",
        str(STACK_ENV_PATH),
        "up",
        "-d",
    ]

    print("Starting system Docker Compose stack...")
    result = subprocess.run(compose_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"{ERR} Failed to start Docker Compose stack:\n{result.stderr}",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    print("Waiting for PostgreSQL to be ready...")
    for attempt in range(30):
        ready = subprocess.run(
            ["docker", "exec", "svs-db", "pg_isready", "-U", "svs"],
            capture_output=True,
            text=True,
        )
        if ready.returncode == 0:
            print(f"{OK} PostgreSQL is ready.")
            return
        time.sleep(2)

    print(f"{ERR} PostgreSQL did not become ready within 60 seconds.", file=sys.stderr)
    raise typer.Exit(code=1)


def _write_svs_env(password: str) -> None:
    """Write the SVS core environment file with DATABASE_URL.

    Security note: the connection URL contains the password in clear text.
    Django needs it to connect to the database. The file is created with
    0o640 (owner read/write, group read) to limit exposure. This is an
    accepted risk in this self-hosted context.

    Args:
        password: The PostgreSQL password.
    """
    db_url = f"postgresql://svs:{password}@localhost:5432/svsdb"
    SVS_ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVS_ENV_PATH.write_text(f"DATABASE_URL={db_url}\n")
    SVS_ENV_PATH.chmod(0o640)
    print(f"{OK} {SVS_ENV_PATH} created.")


def _run_migrations() -> None:
    """Run Django database migrations for the svs_core app."""
    from django.core.management import call_command

    print("Running Django migrations...")
    try:
        call_command("migrate", "svs_core")
        print(f"{OK} Django migrations completed.")
    except Exception as e:
        print(f"{ERR} Failed to run migrations: {e}", file=sys.stderr)
        raise typer.Exit(code=1)


def _find_template_dirs() -> list[Path]:
    """Locate directories containing official service templates.

    Checks (in order):
    1. Package-bundled data directory (via __file__ relative path).
    2. ``importlib.resources`` (modern Python package data API).
    3. System share path (``/usr/local/share/service_templates/``).

    Returns:
        A list of directory paths to scan, in priority order.
    """
    discovered: list[Path] = []

    try:
        rel = Path(__file__).resolve().parent.parent / "data" / "templates"
        if rel.is_dir():
            discovered.append(rel)
    except (NameError, OSError):
        pass

    try:
        pkg_dir = pkg_files("svs_core.data.templates")
        if pkg_dir.is_dir():
            p = Path(str(pkg_dir))
            if p not in discovered:
                discovered.append(p)
    except (ModuleNotFoundError, TypeError, OSError):
        pass

    share = Path("/usr/local/share/service_templates")
    if share.is_dir() and share not in discovered:
        discovered.append(share)

    return discovered


def _import_official_templates() -> None:
    """Import all official templates bundled with the package."""
    from svs_core.docker.template import Template
    from svs_core.shared.exceptions import TemplateException, ValidationException

    candidate_dirs = _find_template_dirs()

    if not candidate_dirs:
        print(f"{WARN} No template directories found. Skipping template import.")
        return

    seen_names: set[tuple[str, str]] = set()
    for template in Template.objects.all():
        seen_names.add((template.name, template.type))

    imported_count = 0
    for templates_dir in candidate_dirs:
        for entry in sorted(templates_dir.iterdir()):
            if entry.suffix.lower() == ".json" and entry.name.lower() != "schema.json":
                if not entry.is_file():
                    continue
                data = json.loads(entry.read_text())
                key = (data.get("name", ""), data.get("type", ""))
                if key in seen_names:
                    continue
                try:
                    Template.import_from_json(data)
                    seen_names.add(key)
                    imported_count += 1
                except (TemplateException, ValidationException) as exc:
                    logger.warning("Skipping template %s: %s", entry.name, exc)

    if imported_count:
        print(f"{OK} Imported {imported_count} official template(s).")
    else:
        print(f"{INFO} No new templates to import.")


def _create_admin_user(password: str | None, non_interactive: bool) -> None:
    """Create the initial admin user if none exists.

    The admin username is always derived from the current OS user
    (detected via ``SystemUserManager.get_system_username()``).

    Args:
        password: Pre-set password (auto mode), or None to prompt / generate.
        non_interactive: If True, generate a random password when none given.
    """
    from svs_core.users.system import SystemUserManager
    from svs_core.users.user import User

    if User.objects.filter(is_superuser=True).exists():
        print(f"{OK} Admin user already exists, skipping.")
        return

    username = SystemUserManager.get_system_username()

    if password:
        try:
            User.create(username, password, True)
            print(f"{OK} Admin user '{username}' created.")
            return
        except Exception as e:
            print(
                f"{e}\nFailed to create user with provided credentials.",
                file=sys.stderr,
            )
            raise typer.Exit(code=1)

    if non_interactive:
        # Generate a random password
        password = secrets.token_urlsafe(12)
        try:
            User.create(username, password, True)
            print(f"{OK} Admin user '{username}' created.")
            print(f"   Password: {password}")
            print(f"   {WARN} Please change this password after first login.")
            return
        except Exception as e:
            print(f"{ERR} Failed to create admin user: {e}", file=sys.stderr)
            raise typer.Exit(code=1)

    # Interactive mode — prompt only for password
    try:
        print()
        print(f"Creating admin user [bold]{username}[/bold].")
        password = getpass("Type your SVS password: ").strip()
        if not password:
            print("Password cannot be empty.", file=sys.stderr)
            raise typer.Exit(code=1)
        User.create(username, password, True)
        print(f"{OK} Admin user '{username}' created.")
    except typer.Exit:
        raise
    except Exception as e:
        print(f"{e}\nFailed to create user, try again")
        _create_admin_user(None, False)


def _install_completions() -> None:
    """Install shell completions for the svs CLI."""
    completions_dir = Path("/usr/share/bash-completion/completions")
    completions_dir.mkdir(parents=True, exist_ok=True)

    comp_path = completions_dir / "svs"
    if comp_path.exists():
        print(f"{OK} Bash completions already installed at {comp_path}.")
        return

    try:
        import subprocess

        result = subprocess.run(
            [sys.executable, "-m", "svs_core", "--show-completion"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            comp_path.write_text(result.stdout)
            comp_path.chmod(0o644)
            print(f"{OK} Bash completions installed at {comp_path}.")
        else:
            print(f"{INFO} Could not generate completions, skipping.")
    except Exception as e:
        logger.debug("Completion installation skipped: %s", e)
        print(f"{INFO} Could not install bash completions, skipping.")


def init_cmd(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Non-interactive mode with defaults."
    ),
    password: str | None = typer.Option(
        None, "--password", help="Admin password (non-interactive mode)."
    ),
    skip_templates: bool = typer.Option(
        False, "--skip-templates", help="Skip official template import."
    ),
    skip_completions: bool = typer.Option(
        False, "--skip-completions", help="Skip bash completion install."
    ),
) -> None:
    """Initialize the SVS environment.

    Creates the Docker Compose stack (PostgreSQL + Caddy), runs database
    migrations, imports official templates, creates an admin user, and
    installs bash completions.

    The admin username is derived from the current OS user
    (handles ``sudo``, ``su``, and direct execution transparently).

    This command is idempotent - running it multiple times is safe.
    Requires root privileges for file operations and Docker access.
    """
    non_interactive = yes or bool(password)

    print("[bold]SVS Environment Initialization[/bold]")
    print("=" * 40)

    _verify_docker()

    pg_password = _setup_docker_compose(non_interactive)

    _start_stack(pg_password)
    _write_svs_env(pg_password)
    from svs_core.shared.env_manager import EnvManager

    os.environ["DATABASE_URL"] = EnvManager.get_database_url()
    _run_migrations()

    if not skip_templates:
        _import_official_templates()
    else:
        print(f"{INFO} Template import skipped.")

    _create_admin_user(password, non_interactive)

    if not skip_completions:
        _install_completions()
    else:
        print(f"{INFO} Completion install skipped.")

    print()
    print(f"{OK} SVS environment initialization complete!")
