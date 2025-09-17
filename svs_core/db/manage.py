#!/usr/bin/env python3

# Dev only script to manage the database schema.
import asyncio
import sys

from dotenv import load_dotenv

from svs_core.docker.network import DockerNetworkManager


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


async def dev_seed() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    from svs_core.users.user import User

    try:
        DockerNetworkManager.delete_network("testuser")
    except Exception:
        pass

    user = await User.create(name="testuser", password="12345678")
    print(user)


if __name__ == "__main__":
    load_dotenv()

    from tortoise import Tortoise

    from svs_core.db.models import TORTOISE_ORM

    action = sys.argv[1] if len(sys.argv) > 1 else None

    if action not in ["init", "clear"]:
        print("Usage: manage.py <init|clear|dev-seed>")
        sys.exit(1)

    match action:
        case "init":
            asyncio.run(init())

        case "clear":
            asyncio.run(clear())

        case "dev-seed":
            asyncio.run(dev_seed())
