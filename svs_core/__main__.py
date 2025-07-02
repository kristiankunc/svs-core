#!/usr/bin/env python3

import asyncio

import typer
from tortoise import Tortoise

from svs_core.cli.user import user_app
from svs_core.db.models import TORTOISE_ORM

app = typer.Typer(help="SVS CLI")

app.add_typer(user_app, name="user")


def main() -> None:
    asyncio.run(Tortoise.init(config=TORTOISE_ORM))
    app()


if __name__ == "__main__":
    main()
