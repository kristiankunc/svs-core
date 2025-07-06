import asyncio

import typer

from svs_core.docker.template import Template
from svs_core.shared.exceptions import AlreadyExistsException

app = typer.Typer(help="Manage Docker templates")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Template name"),
    dockerfile: str = typer.Argument(..., help="Dockerfile content"),
    description: str = typer.Option(None, help="Template description"),
    exposed_ports: str = typer.Option(
        None, help="Comma-separated list of exposed ports"
    ),
) -> None:
    """Create a new template."""

    async def _create():
        ports = (
            [int(p.strip()) for p in exposed_ports.split(",") if p.strip().isdigit()]
            if exposed_ports
            else None
        )
        try:
            template = await Template.create(
                name=name,
                dockerfile=dockerfile,
                description=description,
                exposed_ports=ports if ports else [],
            )
            typer.echo(f"✅ Template '{template.name}' created successfully.")
        except AlreadyExistsException as e:
            typer.echo(f"❌ {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_create())


@app.command("get")
def get(id: int = typer.Argument(..., help="Template ID")) -> None:
    """Get a template by id."""

    async def _get():
        try:
            template = await Template.get_by_id(id)
            if not template:
                typer.echo(f"❌ Template with ID '{id}' not found.", err=True)
                return
            typer.echo(template)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_get())


@app.command("list")
def list_templates() -> None:
    """List all templates."""

    async def _list():
        templates = await Template.get_all()
        if not templates:
            typer.echo("No templates found.")
            return

        typer.echo(f"📦 Total templates: {len(templates)}")
        typer.echo("\n".join(f"- {template}" for template in templates))

    asyncio.run(_list())


@app.command("import-url")
def import_url(url: str = typer.Argument(..., help="URL to Dockerfile")) -> None:
    """Import a template from a Dockerfile URL."""

    async def _import():
        try:
            template = await Template.import_from_url(url)
            typer.echo(f"✅ Imported template: {template}")
        except AlreadyExistsException as e:
            typer.echo(f"❌ {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_import())


@app.command("discover-gh")
def discover_gh(
    repo_url: str = typer.Argument(..., help="GitHub repository URL")
) -> None:
    """Discover templates from a GitHub repository."""

    async def _discover():
        try:
            templates = await Template.discover_from_github(repo_url)
            if not templates:
                typer.echo("No templates discovered in the repository.")
                return
            typer.echo(f"✅ Discovered {len(templates)} template(s):")
            for t in templates:
                typer.echo(f"- {t}")
        except AlreadyExistsException as e:
            typer.echo(f"❌ {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_discover())
