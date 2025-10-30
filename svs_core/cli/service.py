import typer

from svs_core.cli.state import get_current_username, is_current_user_admin
from svs_core.docker.service import Service
from svs_core.users.user import User

app = typer.Typer(help="Manage services")


@app.command("list")
def list_services() -> None:
    """List all services."""

    services: list[Service] = []

    if not is_current_user_admin():
        services = Service.objects.filter(user__name=get_current_username())
    else:
        services = Service.objects.all()

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
) -> None:
    """Create a new service."""

    user = User.objects.get(id=user_id)
    service = Service.create_from_template(name, template_id, user)
    typer.echo(
        f"✅ Service '{service.name}' created successfully with ID {service.id}."
    )


@app.command("start")
def start_service(
    service_id: int = typer.Argument(..., help="ID of the service to start")
) -> None:
    """Start a service."""

    service = Service.objects.get(id=service_id)
    if not service:
        typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
        return

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("❌ You do not have permission to start this service.", err=True)
        return

    service.start()
    typer.echo(f"✅ Service '{service.name}' started successfully.")


@app.command("stop")
def stop_service(
    service_id: int = typer.Argument(..., help="ID of the service to stop")
) -> None:
    """Stop a service."""

    service = Service.objects.get(id=service_id)
    if not service:
        typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
        return

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("❌ You do not have permission to stop this service.", err=True)
        return

    service.stop()
    typer.echo(f"✅ Service '{service.name}' stopped successfully.")


@app.command("delete")
def delete_service(
    service_id: int = typer.Argument(..., help="ID of the service to delete")
) -> None:
    """Delete a service."""

    service = Service.objects.get(id=service_id)
    if not service:
        typer.echo(f"❌ Service with ID {service_id} not found.", err=True)
        return

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("❌ You do not have permission to delete this service.", err=True)
        return

    service.delete()
    typer.echo(f"✅ Service '{service.name}' deleted successfully.")
