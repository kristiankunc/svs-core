import json
import os
import sys

import typer

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

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
        print(f"File '{file_path}' does not exist.", file=sys.stderr)
        raise typer.Exit(code=1)

    with open(file_path, "r") as file:
        data = json.load(file)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Importing template...", total=None)

        template = Template.import_from_json(data)

    print(f"Template '{template.name}' imported successfully.")


@app.command("list")
def list_templates(
    inline: bool = typer.Option(
        False, "-i", "--inline", help="Display templates in inline format"
    )
) -> None:
    """List all available templates."""

    templates = Template.objects.all()

    if len(templates) == 0:
        print("No templates found.")
        raise typer.Exit(code=0)

    if inline:
        print("\n".join(f"{t}" for t in templates))
        raise typer.Exit(code=0)

    table = Table("ID", "Name", "Type", "Description")
    for template in templates:
        table.add_row(
            str(template.id),
            template.name,
            template.type,
            template.description or "-",
        )

    print(table)


@app.command("get")
def get_template(
    template_id: str = typer.Argument(..., help="ID of the template to retrieve")
) -> None:
    """Get a template by ID."""

    template = get_or_exit(Template, id=template_id)

    print(template)


@app.command("delete")
def delete_template(
    template_id: str = typer.Argument(..., help="ID of the template to delete")
) -> None:
    """Delete a template by ID."""

    reject_if_not_admin()

    template = get_or_exit(Template, id=template_id)

    template.delete()
    print(f"Template with ID '{template_id}' deleted successfully.")
