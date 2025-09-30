import asyncio
import json
import os

import typer

from svs_core.docker.template import Template

app = typer.Typer(help="Manage templates")


@app.command("import")
def import_template(
    file_path: str = typer.Argument(..., help="Path to the template file to import")
) -> None:
    """Import a new template from a file"""

    async def _import():
        if not os.path.isfile(file_path):
            typer.echo(f"❌ File '{file_path}' does not exist.", err=True)
            return

        with open(file_path, "r") as file:
            data = json.load(file)

        template = await Template.import_from_json(data)
        typer.echo(f"✅ Template '{template.name}' imported successfully.")

    asyncio.run(_import())


@app.command("list")
def list_templates() -> None:
    """List all available templates"""

    async def _list():
        templates = await Template.get_all()

        if len(templates) == 0:
            typer.echo("No templates found.")
            return

        for template in templates:
            typer.echo(f"- {template}")

    asyncio.run(_list())
