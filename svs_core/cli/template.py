import json
import os
import sys

import typer

from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from svs_core.cli.lib import confirm_action, get_or_exit, template_id_autocomplete
from svs_core.cli.state import reject_if_not_admin
from svs_core.docker.template import Template
from svs_core.shared.exceptions import TemplateException, ValidationException

app = typer.Typer(help="Manage templates")


@app.command("import")
def import_template(
    file_path: str = typer.Argument(..., help="Path to the template file to import"),
    recursive: bool = typer.Option(
        False,
        "-r",
        "--recursive",
        help="Import templates from directories recursively (one level deep)",
    ),
) -> None:
    """Import a new template from a file."""

    reject_if_not_admin()

    if not os.path.exists(file_path):
        print(f"File/directory '{file_path}' does not exist.", file=sys.stderr)
        raise typer.Exit(code=1)

    if recursive and not os.path.isdir(file_path):
        print(
            f"Path '{file_path}' is not a directory for recursive import.",
            file=sys.stderr,
        )
        raise typer.Exit(code=1)

    files = []
    if recursive:
        for entry in os.listdir(file_path):
            full_path = os.path.join(file_path, entry)
            if (
                os.path.isfile(full_path)
                and full_path.lower().endswith(".json")
                and not full_path.lower().endswith("schema.json")
            ):
                files.append(full_path)
    else:
        files.append(file_path)

    for path in files:
        with open(path, "r") as file:
            data = json.load(file)

        skip_import = False
        all_templates = Template.objects.all()
        for existing_template in all_templates:
            if existing_template.name == data.get(
                "name"
            ) and existing_template.type == data.get("type"):
                skip = confirm_action(
                    f"Template '{existing_template.name}' of type '{existing_template.type}' already exists. Skip import?"
                )

                if skip:
                    print(f"Skipping import of template '{data.get('name')}'.")
                    skip_import = True
                break

        if skip_import:
            continue

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            progress.add_task(
                description=f"Importing template/{os.path.basename(path)}...",
                total=None,
            )

            try:
                template = Template.import_from_json(data)
                print(f"Template '{template.name}' imported successfully.")
            except (TemplateException, ValidationException) as e:
                print(f"Error importing template from '{path}': {e}", file=sys.stderr)
                raise typer.Exit(code=1)


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
    template_id: str = typer.Argument(
        ...,
        help="ID of the template to retrieve",
        autocompletion=template_id_autocomplete,
    ),
    long: bool = typer.Option(
        False, "-l", "--long", help="Display full template details"
    ),
) -> None:
    """Get a template by ID."""

    template = get_or_exit(Template, id=template_id)

    if long:
        print(template.__str__())
    else:
        print(template.pprint())


@app.command("delete")
def delete_template(
    template_id: str = typer.Argument(
        ...,
        help="ID of the template to delete",
        autocompletion=template_id_autocomplete,
    )
) -> None:
    """Delete a template by ID."""

    reject_if_not_admin()

    template = get_or_exit(Template, id=template_id)

    template.delete()
    print(f"Template with ID '{template_id}' deleted successfully.")
