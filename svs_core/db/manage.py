#!/usr/bin/env python3

# Dev only script to manage the database schema.
import asyncio
import sys

from tortoise import Tortoise

from svs_core.db.models import TORTOISE_ORM


async def init() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print("Schema generated!")


async def clear() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    conn = Tortoise.get_connection("default")
    for model in Tortoise.apps.get("models", {}).values():
        table = model._meta.db_table
        await conn.execute_script(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
    await Tortoise.close_connections()
    print("All schemas cleared!")

    await init()


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else None

    if action not in ["init", "clear"]:
        print("Usage: manage.py <init|clear>")
        sys.exit(1)

    match action:
        case "init":
            asyncio.run(init())

        case "clear":
            asyncio.run(clear())
