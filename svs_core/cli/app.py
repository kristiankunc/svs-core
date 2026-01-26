from svs_core.cli.utils import app as utils_app
from svs_core.cli.user import app as user_app
from svs_core.cli.template import app as template_app
from svs_core.cli.service import app as service_app
import typer

app = typer.Typer(
    help="SVS CLI",
    pretty_exceptions_enable=False,
)


@app.callback()
def global_options(
    version: bool = typer.Option(
        False,
        "--version",
        help="Show version and exit.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output.",
    ),
    user_override: str | None = typer.Option(
        None,
        "--user",
        "-u",
        help="Override acting user (admin only).",
    ),
) -> None:
    """Global options for the SVS CLI."""
    pass  # runtime logic is injected later


app.add_typer(user_app, name="user")
app.add_typer(template_app, name="template")
app.add_typer(service_app, name="service")
app.add_typer(utils_app, name="utils")
