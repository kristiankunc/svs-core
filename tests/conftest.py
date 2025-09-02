import os
from urllib.parse import urlparse, urlunparse

import pytest_asyncio
from tortoise import Tortoise

# TODO: Analyze this


async def _ensure_postgres_database(db_url: str) -> None:
    """Ensure the target Postgres database exists; create it if missing.

    We connect to the default 'postgres' maintenance DB and attempt a CREATE DATABASE.
    """
    try:
        import asyncpg  # type: ignore
    except Exception:  # pragma: no cover - fallback if asyncpg missing
        return

    parsed = urlparse(db_url)
    if not parsed.scheme.startswith("postgres"):
        return

    target_db = parsed.path.lstrip("/")
    if not target_db:
        return

    # Build admin URL pointing to 'postgres' database instead of target
    admin_path = "/postgres"
    admin_url = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            admin_path,
            parsed.params,
            parsed.query,
            parsed.fragment,
        )
    )

    try:
        conn = await asyncpg.connect(admin_url)
    except Exception:
        # Can't connect; let later code raise a clearer error
        return

    try:
        # Use dynamic identifier quoting
        await conn.execute(f'CREATE DATABASE "{target_db}"')
    except asyncpg.DuplicateDatabaseError:  # type: ignore[attr-defined]
        pass  # Already exists
    except Exception:
        pass  # Non-fatal: test will surface connection issue
    finally:
        await conn.close()


@pytest_asyncio.fixture(autouse=True)
async def initialize_tests():
    """Initialize and teardown the DB per test using the active event loop.

    Per-test initialization avoids cross-event-loop issues in STRICT mode and ensures
    isolation by truncating tables between tests.
    """
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set or empty.")

    config = {
        "connections": {"models": test_db_url},
        "apps": {
            "models": {
                "models": ["svs_core.db.models"],
                "default_connection": "models",
            }
        },
    }
    await _ensure_postgres_database(test_db_url)
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()

    # Truncate all tables to ensure a clean state for each test
    conn = Tortoise.get_connection("models")
    for model in Tortoise.apps.get("models", {}).values():
        table = model._meta.db_table
        # Use TRUNCATE ... CASCADE to reset quickly; ignore errors
        try:
            await conn.execute_script(f'TRUNCATE TABLE "{table}" CASCADE;')
        except Exception:
            pass

    yield

    await Tortoise.close_connections()

    await Tortoise.close_connections()
