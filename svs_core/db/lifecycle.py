from tortoise import Tortoise

from svs_core.db.models import TORTOISE_ORM


async def init() -> None:
    await Tortoise.init(config=TORTOISE_ORM)


async def shutdown() -> None:
    await Tortoise.close_connections()
