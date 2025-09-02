#!/usr/bin/env python3

import asyncio
import os

import typer

if not os.getenv("DATABASE_URL"):
    from dotenv import load_dotenv

    load_dotenv()

# from svs_core.cli.service import app as service_app
# from svs_core.cli.template import app as template_app
from svs_core.cli.user import app as user_app

app = typer.Typer(help="SVS CLI")

app.add_typer(user_app, name="user")
# app.add_typer(template_app, name="template")
# app.add_typer(service_app, name="service")


def main() -> None:
    from tortoise import Tortoise

    from svs_core.db.models import TORTOISE_ORM

    asyncio.run(Tortoise.init(config=TORTOISE_ORM))
    app()


if __name__ == "__main__":
    main()
