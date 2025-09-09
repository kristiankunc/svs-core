import asyncio

from django.apps import AppConfig

from svs_core.db.lifecycle import init as init_db


class AppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app"

    def ready(self):
        try:
            loop = asyncio.get_running_loop()
            asyncio.create_task(self.init_tortoise())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.init_tortoise())
            finally:
                loop.close()

    async def init_tortoise(self):
        await init_db()
