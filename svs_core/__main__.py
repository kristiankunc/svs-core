#!/usr/bin/env python3

import asyncio
import os

import typer

from svs_core.shared.logger import get_logger

if not os.getenv("DATABASE_URL"):
    from dotenv import load_dotenv

    load_dotenv()

    # TODO: Figure out a better way to handle initial configurations
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "postgres://a:a@localhost:1234/testdb"
        get_logger(__name__).warning(
            "DATABASE_URL environment variable not set. Running detached from database."
        )

from svs_core.cli.service import app as service_app
from svs_core.cli.setup import app as setup_app
from svs_core.cli.template import app as template_app
from svs_core.cli.user import app as user_app

app = typer.Typer(help="SVS CLI")

app.add_typer(user_app, name="user")
app.add_typer(setup_app, name="setup")
app.add_typer(template_app, name="template")
app.add_typer(service_app, name="service")


def main() -> None:
    from tortoise import Tortoise

    from svs_core.db.models import TORTOISE_ORM

    asyncio.run(Tortoise.init(config=TORTOISE_ORM))
    app()


if __name__ == "__main__":
    main()
