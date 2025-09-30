from tortoise import Tortoise

from svs_core.db.models import TORTOISE_ORM


async def init() -> None:  # noqa: D103
    await Tortoise.init(config=TORTOISE_ORM)


async def shutdown() -> None:  # noqa: D103
    await Tortoise.close_connections()
