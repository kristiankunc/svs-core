"""CLI commands for managing the SVS web interface.

Provides ``svs web init`` to set up the Django-based web UI from a
release tag matching the currently installed core library version.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

from importlib.metadata import version
from pathlib import Path
from string import Template as StrTemplate

import typer

from rich import print
from rich.prompt import Confirm, Prompt

from svs_core.shared.logger import get_logger

logger = get_logger(__name__)

OK = "[bold green]OK[/bold green]"
INFO = "[bold yellow]INFO[/bold yellow]"
WARN = "[bold yellow]WARN[/bold yellow]"
ERR = "[bold red]ERROR[/bold red]"

REPOSITORY_URL = "https://github.com/kristiankunc/svs-core.git"

SYSTEMD_SERVICE_TEMPLATE = StrTemplate("""\
[Unit]
Description=SVS Web Interface
After=network.target

[Service]
User=root
WorkingDirectory=${working_dir}
ExecStart=${venv_python} -m gunicorn project.wsgi --bind 0.0.0.0:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
""")

app = typer.Typer(help="Manage the SVS web interface")


@app.command()
def init(
    install_dir: str = typer.Option(
        "/opt/svs-web",
        "--dir",
        help="Directory where the web interface will be installed.",
    ),
    domain: str | None = typer.Option(
        None,
        "--domain",
        help="Optional domain for Caddy reverse proxy configuration.",
    ),
    no_systemd: bool = typer.Option(
        False,
        "--no-systemd",
        help="Skip systemd service creation.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Non-interactive mode.",
    ),
    skip_build: bool = typer.Option(
        False,
        "--skip-build",
        help="Skip frontend build (npm ci + vite).",
    ),
) -> None:
    """Set up the SVS web interface.

    Clones the repository at the tag matching the currently installed
    ``svs-core`` version, creates a Python virtual environment, installs
    dependencies, builds the frontend, creates a systemd service, and
    prompts for initial configuration.

    Requires root privileges for directory creation and systemd setup.
    """
    install_path = Path(install_dir)
    print("[bold]SVS Web Interface Setup[/bold]")
    print("=" * 40)

    # 1. Determine installed version
    try:
        svs_version = version("svs-core")
    except Exception:
        svs_version = None

    if not svs_version:
        print(
            f"{ERR} Could not determine installed svs-core version.",
            file=sys.stderr,
        )
        print("   Make sure svs-core is installed via pip/pipx.", file=sys.stderr)
        raise typer.Exit(code=1)

    print(f"{INFO} Detected svs-core version: [bold]{svs_version}[/bold]")

    # 2. Check prerequisites
    _check_prerequisites()

    # 3. Create install directory
    _create_install_dir(install_path)

    # 4. Clone or copy the repository at the matching tag
    _clone_repo(install_path, svs_version)

    # 5. Create virtual environment and install dependencies
    _setup_venv(install_path, svs_version)

    # 6. Build frontend
    if not skip_build:
        _build_frontend(install_path)
    else:
        print(f"{INFO} Frontend build skipped.")

    # 7. Configure environment
    _configure_env(install_path, svs_version, yes, domain)

    # 8. Collect static files
    _collect_static(install_path)

    # 9. Create systemd service
    if not no_systemd:
        _create_systemd_service(install_path)
    else:
        print(f"{INFO} Systemd service creation skipped.")

    print()
    print(f"{OK} SVS web interface setup complete!")
    action = "start and enable" if not no_systemd else "run"
    print()
    print(f"To {action} the service:")
    if not no_systemd:
        print(f"  sudo systemctl enable svs-web")
        print(f"  sudo systemctl start svs-web")
    else:
        print(
            f"  cd {install_path} && sudo {install_path / '.venv' / 'bin' / 'gunicorn'} project.wsgi --bind 0.0.0.0:8000"
        )
    print()
    print("Access the web interface at http://<your-server-ip>:8000")


def _check_prerequisites() -> None:
    """Verify that git, npm, and python3 are available."""
    missing = []
    for cmd in ["git", "npm", "python3"]:
        if (
            subprocess.run(
                ["which", cmd],
                capture_output=True,
            ).returncode
            != 0
        ):
            missing.append(cmd)

    if missing:
        print(
            f"{ERR} Missing prerequisites: {', '.join(missing)}",
            file=sys.stderr,
        )
        print("   Please install them and try again.", file=sys.stderr)
        raise typer.Exit(code=1)
    print(f"{OK} All prerequisites (git, npm, python3) found.")


def _create_install_dir(path: Path) -> None:
    """Create the installation directory.

    Args:
        path: The target install path.
    """
    if path.exists():
        if not path.is_dir():
            print(f"{ERR} {path} exists but is not a directory.", file=sys.stderr)
            raise typer.Exit(code=1)
        print(f"{INFO} Using existing directory {path}.")
    else:
        path.mkdir(parents=True, exist_ok=True)
        print(f"{OK} Created {path}.")


def _clone_repo(install_path: Path, svs_version: str) -> None:
    """Clone the repository at the tag matching the installed version.

    Args:
        install_path: Where to clone into.
        svs_version: The git tag to checkout.
    """
    web_dir = install_path / "web"
    web_dir_src = install_path / "svs-core" / "web"

    # Check if web/ already exists directly in install_path
    if (install_path / "manage.py").exists():
        print(f"{INFO} Web files already present in {install_path}.")
        return

    # If svs-core was cloned but web isn't at the right spot
    if web_dir_src.exists() and (web_dir_src / "manage.py").exists():
        print(f"{INFO} Web files already present in {web_dir_src}.")
        return

    # Clone the repository
    print(f"Cloning svs-core at tag [bold]{svs_version}[/bold]...")
    result = subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "--branch",
            f"v{svs_version}",
            REPOSITORY_URL,
            str(install_path / "svs-core"),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Try without 'v' prefix
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                svs_version,
                REPOSITORY_URL,
                str(install_path / "svs-core"),
            ],
            capture_output=True,
            text=True,
        )
    if result.returncode != 0:
        print(f"{ERR} Failed to clone repository: {result.stderr}", file=sys.stderr)
        print("   Falling back to cloning default branch...")
        result = subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                REPOSITORY_URL,
                str(install_path / "svs-core"),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"{ERR} Clone failed: {result.stderr}", file=sys.stderr)
            raise typer.Exit(code=1)

    # Move web/ contents to install_path
    if web_dir_src.exists():
        import shutil

        for item in web_dir_src.iterdir():
            dest = install_path / item.name
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.unlink()
            shutil.move(str(item), str(install_path))
        # Clean up cloned repo
        shutil.rmtree(install_path / "svs-core", ignore_errors=True)

    print(f"{OK} Web files ready in {install_path}.")


def _setup_venv(install_path: Path, svs_version: str) -> None:
    """Create a virtual environment and install dependencies.

    Args:
        install_path: The web app directory.
        svs_version: Matching svs-core version to install.
    """
    venv_path = install_path / ".venv"
    venv_python = venv_path / "bin" / "python"
    req_file = install_path / "requirements.txt"

    if venv_path.exists() and (venv_path / "bin" / "python").exists():
        print(f"{INFO} Virtual environment already exists at {venv_path}.")
    else:
        print("Creating virtual environment...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True,
        )
        print(f"{OK} Virtual environment created.")

    # Install requirements
    if req_file.exists():
        print("Installing web dependencies...")
        subprocess.run(
            [str(venv_python), "-m", "pip", "install", "-r", str(req_file)],
            check=True,
            capture_output=True,
        )
        print(f"{OK} Web dependencies installed.")

    # Install matching svs-core
    print(f"Installing svs-core=={svs_version} into web venv...")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", f"svs-core=={svs_version}"],
        capture_output=True,
    )
    print(f"{OK} svs-core installed in web venv.")

    # Create logs directory
    logs_path = install_path / "logs"
    logs_path.mkdir(exist_ok=True)
    print(f"{OK} Logs directory ready at {logs_path}.")


def _build_frontend(install_path: Path) -> None:
    """Build the frontend assets using npm and Vite.

    Args:
        install_path: The web app directory.
    """
    frontend_dir = install_path / "frontend"

    if not (frontend_dir / "package.json").exists():
        print(f"{INFO} No frontend/package.json found, skipping frontend build.")
        return

    print("Installing frontend dependencies (npm ci)...")
    result = subprocess.run(
        ["npm", "ci", "--prefix", str(frontend_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"{WARN} npm ci failed: {result.stderr.strip()}")
        print("   Trying npm install instead...")
        subprocess.run(
            ["npm", "install", "--prefix", str(frontend_dir)],
            capture_output=True,
        )

    print("Building frontend (npm run build)...")
    result = subprocess.run(
        ["npm", "run", "build", "--prefix", str(frontend_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"{WARN} Frontend build failed: {result.stderr.strip()}")
        print("   The web app may not have custom assets.")
    else:
        print(f"{OK} Frontend built.")


def _configure_env(
    install_path: Path,
    svs_version: str,
    yes: bool,
    domain: str | None,
) -> None:
    """Create or update the .env file for the web app.

    Args:
        install_path: The web app directory.
        svs_version: The svs-core version (for display).
        yes: Non-interactive mode.
        domain: Optional domain for Caddy config.
    """
    env_example = install_path / ".env.example"
    env_path = install_path / ".env"

    if env_path.exists():
        print(f"{INFO} {env_path} already exists, keeping existing configuration.")
        return

    if not env_example.exists():
        print(f"{WARN} No .env.example found, creating minimal .env.")
        _write_minimal_env(env_path, domain)
        return

    if yes:
        # Auto-configure from example
        import shutil

        shutil.copy2(str(env_example), str(env_path))
        env_path.chmod(0o600)
        print(f"{OK} Created {env_path} from .env.example.")
        print(f"   {WARN} Please review and update the configuration.")
    else:
        import shutil

        shutil.copy2(str(env_example), str(env_path))
        env_path.chmod(0o600)
        print(f"{OK} Created {env_path} from .env.example.")
        print()
        print("Please edit the .env file with your desired configuration:")
        print(f"  nano {env_path}")
        print()
        if domain:
            _write_caddy_config(install_path, domain)


def _write_minimal_env(env_path: Path, domain: str | None) -> None:
    """Write a minimal .env file when no example is available.

    Security note: the secret key is stored in clear text because Django
    reads it from the environment at startup. The file is created with
    0o600 (owner read/write only) to limit exposure. This is standard
    practice for Django deployments and an accepted risk.

    Args:
        env_path: Path to write the .env file.
        domain: Optional domain for ALLOWED_HOSTS.
    """
    import secrets

    secret_key = secrets.token_urlsafe(50)
    host = domain or "localhost,127.0.0.1"
    content = (
        f"DJANGO_SECRET_KEY={secret_key}\n"
        f"DJANGO_DEBUG=False\n"
        f"DJANGO_ALLOWED_HOSTS={host}\n"
    )
    if domain:
        content += f"DJANGO_CSRF_TRUSTED_ORIGINS=https://{domain}\n"
    env_path.write_text(content)
    env_path.chmod(0o600)
    print(f"{OK} Created minimal {env_path}.")


def _write_caddy_config(install_path: Path, domain: str) -> None:
    """Write a Caddyfile snippet for reverse proxying the web app.

    Args:
        install_path: The web app directory.
        domain: The domain name to configure.
    """
    caddyfile_path = install_path / "web.Caddyfile"
    content = f"{domain} {{\n    reverse_proxy host.docker.internal:8000\n}}\n"
    caddyfile_path.write_text(content)
    print(f"{OK} Created {caddyfile_path} for domain '{domain}'.")
    print()
    print("To use this Caddyfile, mount it in your Caddy container and")
    print("set CADDY_DOCKER_CADDYFILE_PATH. See web setup docs for details.")


def _collect_static(install_path: Path) -> None:
    """Run Django's collectstatic to gather static files.

    Args:
        install_path: The web app directory.
    """
    manage_py = install_path / "manage.py"
    venv_python = install_path / ".venv" / "bin" / "python"

    if not manage_py.exists():
        print(f"{WARN} No manage.py found, skipping collectstatic.")
        return

    print("Collecting static files...")
    result = subprocess.run(
        [str(venv_python), "manage.py", "collectstatic", "--noinput", "--clear"],
        capture_output=True,
        text=True,
        cwd=str(install_path),
    )
    if result.returncode == 0:
        print(f"{OK} Static files collected.")
    else:
        print(f"{WARN} collectstatic note: {result.stderr.strip()}")


def _create_systemd_service(install_path: Path) -> None:
    """Create a systemd service file for the web interface.

    Args:
        install_path: The web app directory.
    """
    service_path = Path("/etc/systemd/system/svs-web.service")
    venv_python = str(install_path / ".venv" / "bin" / "python")

    if service_path.exists():
        print(f"{INFO} {service_path} already exists.")
        if not Confirm.ask("Overwrite?"):
            print("Skipping systemd service creation.")
            return

    content = SYSTEMD_SERVICE_TEMPLATE.substitute(
        working_dir=str(install_path),
        venv_python=venv_python,
    )
    service_path.write_text(content)
    service_path.chmod(0o644)
    print(f"{OK} Created {service_path}.")

    # Reload systemd
    subprocess.run(["systemctl", "daemon-reload"], capture_output=True)
    print(f"{OK} systemd daemon reloaded.")
