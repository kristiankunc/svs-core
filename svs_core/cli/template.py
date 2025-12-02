import json
import os

import typer

from rich.progress import Progress, SpinnerColumn, TextColumn

from svs_core.cli.lib import get_or_exit
from svs_core.cli.state import reject_if_not_admin
from svs_core.docker.template import Template

app = typer.Typer(help="Manage templates")


@app.command("import")
def import_template(
    file_path: str = typer.Argument(..., help="Path to the template file to import")
) -> None:
    """Import a new template from a file."""

    reject_if_not_admin()

    if not os.path.isfile(file_path):
        typer.echo(f"File '{file_path}' does not exist.", err=True)
        raise typer.Exit(code=1)

    with open(file_path, "r") as file:
        data = json.load(file)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Importing template...", total=None)

        template = Template.import_from_json(data)

    typer.echo(f"Template '{template.name}' imported successfully.")


@app.command("list")
def list_templates() -> None:
    """List all available templates."""

    templates = Template.objects.all()

    if len(templates) == 0:
        typer.echo("No templates found.")
        raise typer.Exit(code=0)

    typer.echo("\n".join(f"{t}" for t in templates))


@app.command("get")
def get_template(
    template_id: str = typer.Argument(..., help="ID of the template to retrieve")
) -> None:
    """Get a template by ID."""

    template = get_or_exit(Template, id=template_id)

    typer.echo(template)


@app.command("delete")
def delete_template(
    template_id: str = typer.Argument(..., help="ID of the template to delete")
) -> None:
    """Delete a template by ID."""

    reject_if_not_admin()

    template = get_or_exit(Template, id=template_id)

    template.delete()
    typer.echo(f"✅ Template with ID '{template_id}' deleted successfully.")
