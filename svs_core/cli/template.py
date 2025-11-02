import json
import os

import typer

from svs_core.docker.template import Template

app = typer.Typer(help="Manage templates")


@app.command("import")
def import_template(
    file_path: str = typer.Argument(..., help="Path to the template file to import")
) -> None:
    """Import a new template from a file."""

    if not os.path.isfile(file_path):
        typer.echo(f"❌ File '{file_path}' does not exist.", err=True)
        return

    with open(file_path, "r") as file:
        data = json.load(file)

    template = Template.import_from_json(data)
    typer.echo(f"✅ Template '{template.name}' imported successfully.")


@app.command("list")
def list_templates() -> None:
    """List all available templates."""

    templates = Template.objects.all()

    if len(templates) == 0:
        typer.echo("No templates found.")
        return

    for template in templates:
        typer.echo(f"- {template}")


@app.command("delete")
def delete_template(
    template_id: str = typer.Argument(..., help="ID of the template to delete")
) -> None:
    """Delete a template by ID."""

    template = Template.objects.get(id=template_id)
    if not template:
        typer.echo(f"❌ Template with ID '{template_id}' not found.", err=True)
        return

    template.delete()
    typer.echo(f"✅ Template with ID '{template_id}' deleted successfully.")
