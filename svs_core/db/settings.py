import os

import dj_database_url

from svs_core.shared.env_manager import EnvManager

ENVIRONMENT = (
    EnvManager.get_runtime_environment() == EnvManager.RuntimeEnvironment.DEVELOPMENT
)
SECRET_KEY = "library-dummy-key"

INSTALLED_APPS = [
    "svs_core.apps.SvsCoreConfig",
]

database_url = EnvManager.get_database_url()
DATABASES = {"default": dj_database_url.parse(database_url)}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

TIME_ZONE = "UTC"
USE_TZ = True
DEBUG = ENVIRONMENT == "dev"
MIGRATION_MODULES = {"svs_core": "svs_core.db.migrations"}
