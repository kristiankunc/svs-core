"""CLI command for destroying (uninstalling) the SVS environment.

Reverses everything that ``svs init`` sets up: stops Docker services,
removes volumes, deletes configuration files, removes system users,
and cleans up sudoers entries.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys

import typer

from rich import print
from rich.prompt import Confirm

from svs_core.shared.logger import get_logger

logger = get_logger(__name__)

# Styled log prefixes (Rich markup - no emojis)
OK = "[bold green]OK[/bold green]"
INFO = "[bold yellow]INFO[/bold yellow]"
WARN = "[bold yellow]WARN[/bold yellow]"
ERR = "[bold red]ERROR[/bold red]"

SVS_CONFIG_DIR = "/etc/svs"
SVS_DATA_DIR = "/var/svs"
COMPOSE_PATH = "/etc/svs/docker/docker-compose.yml"
STACK_ENV_PATH = "/etc/svs/docker/stack.env"
SUDOERS_MARKER_BEGIN = "# --- SVS begin ---"
SUDOERS_MARKER_END = "# --- SVS end ---"


def _stop_user_services() -> None:
    """Stop and remove all Docker services managed by SVS."""
    from svs_core.db.models import ServiceModel

    services = ServiceModel.objects.all()
    if not services:
        print(f"{INFO} No user services to stop.")
        return

    print(f"Stopping {len(services)} user service(s)...")
    for service in services:
        container_id = service.container_id
        if container_id:
            subprocess.run(
                ["docker", "rm", "-f", container_id],
                capture_output=True,
            )
            print(f"  - Removed container {container_id} for service '{service.name}'.")
    print(f"{OK} All user services stopped.")


def _stop_system_stack() -> None:
    """Stop and remove the system Docker Compose stack (PostgreSQL + Caddy)."""
    if not os.path.exists(COMPOSE_PATH):
        print(f"{INFO} No system Docker Compose stack found.")
        return

    print("Stopping system Docker Compose stack...")
    result = subprocess.run(
        [
            "docker",
            "compose",
            "-f",
            COMPOSE_PATH,
            "--env-file",
            STACK_ENV_PATH,
            "down",
            "--remove-orphans",
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"{OK} System Docker Compose stack stopped.")
    else:
        print(f"{WARN} Could not stop stack: {result.stderr.strip()}")


def _remove_volumes(keep_volumes: bool) -> None:
    """Remove Docker volumes created by the system stack.

    Args:
        keep_volumes: If True, skip volume removal.
    """
    if keep_volumes:
        print(f"{INFO} Keeping Docker volumes (--keep-volumes).")
        return

    # Remove named volumes used by the stack
    for volume in ["svs-core_pgdata", "svs-core_caddy_data", "svs-core_caddy_config"]:
        subprocess.run(
            ["docker", "volume", "rm", "-f", volume],
            capture_output=True,
        )
    print(f"{OK} Docker volumes removed.")


def _remove_config_dirs() -> None:
    """Remove /etc/svs and /var/svs directories."""
    for path in [SVS_CONFIG_DIR, SVS_DATA_DIR]:
        if os.path.exists(path):
            shutil.rmtree(path, ignore_errors=True)
            print(f"{OK} Removed {path}.")

    # Also remove the log file if left behind
    log_path = "/etc/svs/svs.log"
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except OSError:
            pass


def _clean_sudoers() -> None:
    """Remove svs-related entries from /etc/sudoers."""
    sudoers_path = "/etc/sudoers"
    if not os.path.exists(sudoers_path):
        return

    try:
        with open(sudoers_path) as f:
            content = f.read()
    except PermissionError:
        print(f"{WARN} Cannot read /etc/sudoers -- skipping sudoers cleanup.")
        return

    lines_to_remove = [
        "ALL ALL=NOPASSWD: /usr/local/bin/svs",
        "%svs-admins ALL=(svs) NOPASSWD: /usr/local/bin/svs",
    ]

    new_lines = []
    removed = 0
    for line in content.splitlines(keepends=True):
        stripped = line.strip()
        if any(target in stripped for target in lines_to_remove):
            removed += 1
        else:
            new_lines.append(line)

    if removed:
        try:
            import tempfile

            fd, tmp_path = tempfile.mkstemp()
            with os.fdopen(fd, "w") as f:
                f.writelines(new_lines)
            shutil.move(tmp_path, sudoers_path)
            print(f"{OK} Removed {removed} sudoers entr(ies).")
        except PermissionError:
            print(f"{WARN} Cannot write /etc/sudoers -- sudoers cleanup skipped.")
    else:
        print(f"{INFO} No SVS sudoers entries found.")


def _remove_system_user() -> None:
    """Remove the svs system user and svs-admins group."""
    import grp
    import pwd

    # Remove svs user
    try:
        pwd.getpwnam("svs")
        subprocess.run(
            ["userdel", "-f", "svs"],
            capture_output=True,
        )
        print(f"{OK} Removed system user 'svs'.")
    except KeyError:
        print(f"{INFO} System user 'svs' does not exist.")

    # Remove svs-admins group
    try:
        grp.getgrnam("svs-admins")
        subprocess.run(
            ["groupdel", "svs-admins"],
            capture_output=True,
        )
        print(f"{OK} Removed group 'svs-admins'.")
    except KeyError:
        print(f"{INFO} Group 'svs-admins' does not exist.")


def _uninstall_pipx_package() -> None:
    """Uninstall the svs-core package via pipx."""
    print("Uninstalling svs-core via pipx...")
    result = subprocess.run(
        ["pipx", "uninstall", "svs-core"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print(f"{OK} svs-core uninstalled via pipx.")
    else:
        print(f"{WARN} pipx uninstall note: {result.stderr.strip()}")


def destroy_cmd(
    yes: bool = typer.Option(
        False, "--yes", "-y", help="Skip all confirmation prompts."
    ),
    keep_volumes: bool = typer.Option(
        False, "--keep-volumes", help="Preserve Docker volumes."
    ),
    keep_config: bool = typer.Option(
        False, "--keep-config", help="Preserve config files."
    ),
    uninstall_package: bool = typer.Option(
        False,
        "--uninstall-package",
        help="Also uninstall svs-core via pipx.",
    ),
) -> None:
    """Destroy the SVS environment.

    Reverses ``svs init``: stops all services, removes the Docker Compose
    stack, deletes volumes, configuration, system users, and sudoers entries.

    Use with caution - this operation is destructive and cannot be undone.
    """
    print("[bold red]SVS Environment Destruction[/bold red]")
    print("=" * 40)
    print()
    print("This will remove all SVS data, including Docker containers,")
    print("volumes, configuration files, system users, and sudoers entries.")
    print()

    if not yes:
        confirmed = Confirm.ask(
            "Are you sure you want to destroy the SVS environment?",
            default=False,
        )
        if not confirmed:
            print("Aborted.")
            raise typer.Exit(code=0)

    _stop_user_services()
    _stop_system_stack()
    _remove_volumes(keep_volumes)

    if not keep_config:
        _remove_config_dirs()
    else:
        print(f"{INFO} Keeping config files (--keep-config).")

    _clean_sudoers()
    _remove_system_user()

    if uninstall_package:
        _uninstall_pipx_package()

    print()
    print("[bold red]SVS environment has been destroyed.[/bold red]")
