import asyncio
import os

import pytest
import pytest_asyncio
from tortoise import Tortoise


async def _setup_postgres_database(db_url):
    """Create the test database if it doesn't exist."""
    if not db_url or not db_url.startswith("postgres"):
        return

    try:
        import asyncpg

        # Extract database name from URL
        db_name = db_url.split("/")[-1].split("?")[0]
        if not db_name:
            return

        # Create admin connection URL
        admin_url = db_url.replace(f"/{db_name}", "/postgres")

        # Connect to postgres database
        conn = await asyncpg.connect(admin_url)

        # Drop existing database if any
        try:
            # Terminate active connections
            await conn.execute(
                f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
                """
            )
            await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        except Exception:
            pass

        # Create the database
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        await conn.close()
    except Exception as e:
        print(f"Database setup error: {e}")


@pytest.fixture
def event_loop():
    """Create a fresh event loop for each test."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create a test database once at the beginning of the test session."""
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")

    await _setup_postgres_database(test_db_url)
    yield


@pytest_asyncio.fixture(autouse=True)
async def initialize_tortoise():
    """Initialize Tortoise ORM for each test with a clean database state."""
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")

    # Configure Tortoise ORM
    config = {
        "connections": {"models": test_db_url},
        "apps": {
            "models": {
                "models": ["svs_core.db.models"],
                "default_connection": "models",
            }
        },
    }

    # Initialize Tortoise and create schemas
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas(safe=True)

    # Clean tables for a fresh state
    conn = Tortoise.get_connection("models")
    for model in Tortoise.apps.get("models", {}).values():
        if hasattr(model._meta, "db_table"):
            try:
                await conn.execute_script(
                    f'TRUNCATE TABLE "{model._meta.db_table}" CASCADE;'
                )
            except Exception:
                pass

    yield
    await Tortoise.close_connections()
