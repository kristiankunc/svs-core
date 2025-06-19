# Dev only script to force apply schema to the database.
import asyncio

from tortoise import Tortoise

from svs_core.db.client import TORTOISE_ORM


async def _init() -> None:
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    print("Schema generated!")


if __name__ == "__main__":
    asyncio.run(_init())
