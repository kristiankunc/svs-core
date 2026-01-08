import sys

from pathlib import Path

import typer

from django.core import management
from rich import print as rprint

from svs_core.cli.state import reject_if_not_admin

app = typer.Typer(help="Utility commands")


@app.command("format-dockerfile")
def format_dockerfile(
    dockerfile_path: Path = typer.Argument(..., help="Path to the Dockerfile to format")
) -> None:
    """Formats Dockerfile into a single line string for embedding in JSON."""

    if not dockerfile_path.exists() or not dockerfile_path.is_file():
        rprint(
            "The specified Dockerfile does not exist or is not a file.", file=sys.stderr
        )
        raise typer.Exit(code=1)

    try:
        with dockerfile_path.open("r") as file:
            dockerfile_content = file.read()
    except Exception as e:
        rprint(f"Error reading Dockerfile: {e}", file=sys.stderr)
        raise typer.Exit(code=1)

    formatted_content = (
        dockerfile_content.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )
    print(formatted_content)


@app.command("django-shell")
def django_shell(
    commands: list[str] = typer.Argument(
        ..., help="Django management commands and arguments"
    )
) -> None:
    """Executes Django management commands in a shell environment."""

    reject_if_not_admin()

    if not commands:
        rprint("No commands provided", file=sys.stderr)
        raise typer.Exit(code=1)

    try:
        management.call_command(*commands)
    except Exception as e:
        rprint(f"Error executing Django shell commands: {e}", file=sys.stderr)
        raise typer.Exit(code=1)
