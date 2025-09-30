import asyncio

import typer

from svs_core.docker.service import Service

app = typer.Typer(help="Manage services")


@app.command("list")
def list_services() -> None:
    """List all services."""

    async def _list():
        services = await Service.get_all()

        if len(services) == 0:
            typer.echo("No services found.")
            return

        for service in services:
            typer.echo(f"- {service}")

    asyncio.run(_list())


@app.command("create")
def create_service(
    name: str = typer.Argument(..., help="Name of the service to create"),
    template_id: int = typer.Argument(..., help="ID of the template to use"),
    user_id: int = typer.Argument(..., help="ID of the user creating the service"),
    # TODO: Add override options for all args
) -> None:
    """Create a new service."""

    async def _create():
        service = await Service.create_from_template(name, template_id, user_id)
        typer.echo(
            f"✅ Service '{service.name}' created successfully with ID {service.id}."
        )

    asyncio.run(_create())


@app.command("start")
def start_service(
    service_id: int = typer.Argument(..., help="ID of the service to start")
) -> None:
    """Start a service."""

    async def _start():
        service = await Service.get_by_id(service_id)
        if not service:
            typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
            return

        await service.start()
        typer.echo(f"✅ Service '{service.name}' started successfully.")

    asyncio.run(_start())


@app.command("stop")
def stop_service(
    service_id: int = typer.Argument(..., help="ID of the service to stop")
) -> None:
    """Stop a service."""

    async def _stop():
        service = await Service.get_by_id(service_id)
        if not service:
            typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
            return

        await service.stop()
        typer.echo(f"✅ Service '{service.name}' stopped successfully.")

    asyncio.run(_stop())
