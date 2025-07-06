import asyncio

import typer

from svs_core.docker.service import Service
from svs_core.shared.exceptions import AlreadyExistsException

app = typer.Typer(help="Manage Docker services")


@app.command("create")
def create(
    name: str = typer.Argument(..., help="Service name"),
    template_id: int = typer.Argument(..., help="Template ID"),
    user_id: int = typer.Argument(..., help="User ID"),
    domain: str = typer.Option(None, help="Domain for the service"),
) -> None:
    """Create a new service."""

    async def _create():
        try:
            service = await Service.create(
                name=name,
                template_id=template_id,
                user_id=user_id,
                domain=domain,
            )
            typer.echo(f"✅ Service '{service.name}' created successfully.")
        except AlreadyExistsException as e:
            typer.echo(f"❌ {e}", err=True)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_create())


@app.command("get")
def get(id: int = typer.Argument(..., help="Service ID")) -> None:
    """Get a service by id."""

    async def _get():
        try:
            service = await Service.get_by_id(id)
            if not service:
                typer.echo(f"❌ Service with ID '{id}' not found.", err=True)
                return
            typer.echo(service)
        except Exception as e:
            typer.echo(f"❌ {e}", err=True)

    asyncio.run(_get())


@app.command("list")
def list_services() -> None:
    """List all services."""

    async def _list():
        services = await Service.get_all()
        if not services:
            typer.echo("No services found.")
            return

        typer.echo(f"📋 Total services: {len(services)}")
        typer.echo("".join(f"- {service}\n" for service in services))

    asyncio.run(_list())
