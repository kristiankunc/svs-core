import asyncio

import typer

from svs_core.docker.service import Service

app = typer.Typer(help="Manage services")


@app.command("list")
def list_services() -> None:
    """List all services"""

    async def _list():
        services = await Service.get_all()

        if len(services) == 0:
            typer.echo("No services found.")
            return

        for service in services:
            typer.echo(f"- {service}")

    asyncio.run(_list())
