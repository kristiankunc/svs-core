import os

import dj_database_url

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").lower()
SECRET_KEY = "library-dummy-key"

INSTALLED_APPS = [
    "svs_core.apps.SvsCoreConfig",
]


# Pick DB based on environment
database_url = os.getenv("DATABASE_URL")

DATABASES = {"default": dj_database_url.parse(database_url)}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

TIME_ZONE = "UTC"
USE_TZ = True
DEBUG = ENVIRONMENT == "dev"
