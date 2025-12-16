import sys

from pathlib import Path

import typer

from rich import print as rprint
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from svs_core.cli.lib import get_or_exit
from svs_core.cli.state import get_current_username, is_current_user_admin
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Label,
    Volume,
)
from svs_core.docker.service import Service
from svs_core.users.user import User

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
