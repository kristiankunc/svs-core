import os

import dj_database_url
import django

from django.conf import settings

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").lower()
TEST = os.getenv("TEST", "false").lower() == "true"
SECRET_KEY = "library-dummy-key"

INSTALLED_APPS = [
    "svs_core.db",  # must be a real app package
]


# Pick DB based on environment
database_url = os.getenv("DATABASE_URL")
if TEST:
    database_url = os.getenv("TEST_DATABASE_URL") or database_url

DATABASES = {"default": dj_database_url.parse(database_url)}

CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

TIME_ZONE = "UTC"
USE_TZ = True
DEBUG = ENVIRONMENT == "dev"


def setup_django():
    """Configure Django and initialize apps registry."""
    if not settings.configured:
        settings.configure(
            SECRET_KEY=SECRET_KEY,
            DEBUG=DEBUG,
            INSTALLED_APPS=INSTALLED_APPS,
            DATABASES=DATABASES,
            TIME_ZONE=TIME_ZONE,
            USE_TZ=USE_TZ,
            CACHES=CACHES,
        )

    if not django.apps.apps.ready:
        django.setup()
