import os
from typing import Any, Dict

from svs_core.shared.logger import get_logger

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    get_logger(__name__).error(
        "DATABASE_URL environment variable is not set. Using default SQLite in-memory database."
    )


TORTOISE_ORM: Dict[str, Any] = {
    "connections": {"default": DB_URL},
    "apps": {
        "models": {
            "models": ["aerich.models", "svs_core.db.models"],
            "default_connection": "default",
        },
    },
}
