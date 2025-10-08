import typer

from svs_core.docker.service import Service

app = typer.Typer(help="Manage services")


@app.command("list")
def list_services() -> None:
    """List all services."""
    services = Service.get_all()

    if len(services) == 0:
        typer.echo("No services found.")
        return

    for service in services:
        typer.echo(f"- {service}")


@app.command("create")
def create_service(
    name: str = typer.Argument(..., help="Name of the service to create"),
    template_id: int = typer.Argument(..., help="ID of the template to use"),
    user_id: int = typer.Argument(..., help="ID of the user creating the service"),
    # TODO: Add override options for all args
) -> None:
    """Create a new service."""
    service = Service.create_from_template(name, template_id, user_id)
    typer.echo(
        f"✅ Service '{service.name}' created successfully with ID {service.id}."
    )


@app.command("start")
def start_service(
    service_id: int = typer.Argument(..., help="ID of the service to start")
) -> None:
    """Start a service."""
    service = Service.get_by_id(service_id)
    if not service:
        typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
        return

    service.start()
    typer.echo(f"✅ Service '{service.name}' started successfully.")


@app.command("stop")
def stop_service(
    service_id: int = typer.Argument(..., help="ID of the service to stop")
) -> None:
    """Stop a service."""
    service = Service.get_by_id(service_id)
    if not service:
        typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
        return

    service.stop()
    typer.echo(f"✅ Service '{service.name}' stopped successfully.")
