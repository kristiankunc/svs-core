#!/usr/bin/env python3

import asyncio
import os
import sys

import typer

if not os.getenv("DATABASE_URL"):
    from dotenv import load_dotenv

    load_dotenv()


from svs_core.cli.setup import app as setup_app
from svs_core.cli.user import app as user_app

app = typer.Typer(help="SVS CLI")

app.add_typer(user_app, name="user")
app.add_typer(setup_app, name="setup")


def main() -> None:
    # Skip database initialization if command is init
    if len(sys.argv) > 1 and "init" in sys.argv:
        app()
        return

    from tortoise import Tortoise

    from svs_core.db.models import TORTOISE_ORM

    asyncio.run(Tortoise.init(config=TORTOISE_ORM))
    app()


if __name__ == "__main__":
    main()
