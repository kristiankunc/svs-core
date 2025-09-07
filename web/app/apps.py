import asyncio

from django.apps import AppConfig

from svs_core.db.lifecycle import init as init_db


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        asyncio.create_task(self.init_tortoise())

    async def init_tortoise(self):
        await init_db()
