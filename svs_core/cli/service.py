from pathlib import Path

import typer

from rich.progress import Progress, SpinnerColumn, TextColumn

from svs_core.cli.lib import get_or_exit
from svs_core.cli.state import get_current_username, is_current_user_admin
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Label,
    Volume,
)
from svs_core.docker.service import Service
from svs_core.users.user import User

app = typer.Typer(help="Manage services")


@app.command("list")
def list_services() -> None:
    """List all services."""

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
    domain: str | None = typer.Option(
        None, "--domain", "-d", help="Domain for the service"
    ),
    env: list[str] | None = typer.Option(
        None,
        "--env",
        "-e",
        help="Environment variables in KEY=VALUE format (can be used multiple times)",
    ),
    port: list[str] | None = typer.Option(
        None,
        "--port",
        "-p",
        help="Port mappings in container_port:host_port format (can be used multiple times)",
    ),
    volume: list[str] | None = typer.Option(
        None,
        "--volume",
        "-v",
        help="Volume mappings in container_path:host_path format (can be used multiple times)",
    ),
    label: list[str] | None = typer.Option(
        None,
        "--label",
        "-l",
        help="Labels in KEY=VALUE format (can be used multiple times)",
    ),
    command: str | None = typer.Option(
        None, "--command", "-c", help="Command to run in the container"
    ),
    args: list[str] | None = typer.Option(
        None,
        "--args",
        "-a",
        help="Command arguments (can be used multiple times)",
    ),
) -> None:
    """Create a new service.

    Supports overriding template defaults with command-line options:
    - Environment variables: --env KEY=VALUE
    - Ports: --port container_port:host_port
    - Volumes: --volume container_path:host_path
    - Labels: --label KEY=VALUE
    - Command: --command "command"
    - Arguments: --args "arg1" --args "arg2"
    """

    user = get_or_exit(User, name=get_current_username())

    # Parse environment variables
    override_env = None
    if env:
        override_env = []
        for env_var in env:
            if "=" not in env_var:
                typer.echo(
                    f"Invalid environment variable format: {env_var}. Use KEY=VALUE",
                    err=True,
                )
                raise typer.Exit(code=1)
            key, value = env_var.split("=", 1)
            override_env.append(EnvVariable(key=key, value=value))

    # Parse ports
    override_ports = None
    if port:
        override_ports = []
        for port_mapping in port:
            if ":" not in port_mapping:
                typer.echo(
                    f"Invalid port format: {port_mapping}. Use container_port:host_port",
                    err=True,
                )
                raise typer.Exit(code=1)
            try:
                container_port_str, host_port_str = port_mapping.split(":", 1)
                container_port = int(container_port_str)
                host_port = int(host_port_str)
                override_ports.append(
                    ExposedPort(container_port=container_port, host_port=host_port)
                )
            except ValueError:
                typer.echo(
                    f"Invalid port numbers: {port_mapping}. Ports must be integers",
                    err=True,
                )
                raise typer.Exit(code=1)

    # Parse volumes
    override_volumes = None
    if volume:
        override_volumes = []
        for volume_mapping in volume:
            if ":" not in volume_mapping:
                typer.echo(
                    f"Invalid volume format: {volume_mapping}. Use container_path:host_path",
                    err=True,
                )
                raise typer.Exit(code=1)
            container_path, host_path = volume_mapping.split(":", 1)
            override_volumes.append(
                Volume(container_path=container_path, host_path=host_path)
            )

    # Parse labels
    override_labels = None
    if label:
        override_labels = []
        for lbl in label:
            if "=" not in lbl:
                typer.echo(f"Invalid label format: {lbl}. Use KEY=VALUE", err=True)
                raise typer.Exit(code=1)
            key, value = lbl.split("=", 1)
            override_labels.append(Label(key=key, value=value))

    service = Service.create_from_template(
        name,
        template_id,
        user,
        domain=domain,
        override_env=override_env,
        override_ports=override_ports,
        override_volumes=override_volumes,
        override_command=command,
        override_labels=override_labels,
        override_args=args,
    )
    typer.echo(f"Service '{service.name}' created successfully with ID {service.id}.")


@app.command("start")
def start_service(
    service_id: int = typer.Argument(..., help="ID of the service to start")
) -> None:
    """Start a service."""

    service = get_or_exit(Service, id=service_id)

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("You do not have permission to start this service.", err=True)
        raise typer.Exit(1)

    service.start()
    typer.echo(f"Service '{service.name}' started successfully.")


@app.command("stop")
def stop_service(
    service_id: int = typer.Argument(..., help="ID of the service to stop")
) -> None:
    """Stop a service."""

    service = get_or_exit(Service, id=service_id)

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("You do not have permission to stop this service.", err=True)
        raise typer.Exit(1)

    service.stop()
    typer.echo(f"Service '{service.name}' stopped successfully.")


@app.command("build")
def build_service(
    service_id: int = typer.Argument(..., help="ID of the service to build"),
    path: str = typer.Argument(
        ..., help="Path to the source code to build the service from"
    ),
) -> None:
    """Build a service's Docker image from source code."""

    service = get_or_exit(Service, id=service_id)

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("You do not have permission to build this service.", err=True)
        raise typer.Exit(1)

    path_obj = Path(path)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        progress.add_task(description="Building service...", total=None)

    service.build(path_obj)
    typer.echo(f"Service '{service.name}' Docker image built successfully.")


@app.command("delete")
def delete_service(
    service_id: int = typer.Argument(..., help="ID of the service to delete")
) -> None:
    """Delete a service."""

    service = get_or_exit(Service, id=service_id)

    if not is_current_user_admin() and service.user.name != get_current_username():
        typer.echo("You do not have permission to delete this service.", err=True)
        raise typer.Exit(1)

    service.delete()
    typer.echo(f"Service '{service.name}' deleted successfully.")
