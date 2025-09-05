import asyncio
import os
import platform
import sys
from urllib.parse import urlparse, urlunparse

import pytest
import pytest_asyncio
from tortoise import Tortoise

# Fix for Windows asyncio issues - ensure this is set globally
if sys.platform == "win32" or platform.system() == "Windows":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Set the default scope for pytest-asyncio fixtures to function level
# This ensures each test gets a fresh event loop
pytestmark = pytest.mark.asyncio


async def _ensure_postgres_database(db_url: str, drop_if_exists: bool = False) -> None:
    """Ensure the target Postgres database exists; create it if missing.

    If drop_if_exists is True, it will drop the database if it exists and recreate it.

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
        # If dropping is requested, try to drop the database first
        if drop_if_exists:
            try:
                # Terminate existing connections to the database
                await conn.execute(
                    f"""
                    SELECT pg_terminate_backend(pg_stat_activity.pid)
                    FROM pg_stat_activity
                    WHERE pg_stat_activity.datname = '{target_db}'
                    AND pid <> pg_backend_pid()
                    """
                )
                # Drop the database
                await conn.execute(f'DROP DATABASE IF EXISTS "{target_db}"')
                print(f"Dropped database {target_db}")
            except Exception as e:
                print(f"Error dropping database: {str(e)}")

        # Create the database
        await conn.execute(f'CREATE DATABASE "{target_db}"')
    except asyncpg.DuplicateDatabaseError:  # type: ignore[attr-defined]
        pass  # Already exists
    except Exception as e:
        print(f"Error creating database: {str(e)}")
        pass  # Non-fatal: test will surface connection issue
    finally:
        await conn.close()


# Create a function-scoped event loop for each test
# This is important for Windows compatibility
@pytest.fixture
def event_loop():
    """Create a new event loop for each test function."""
    # For Windows, explicitly use WindowsSelectorEventLoop for network operations
    if sys.platform == "win32" or platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Create and set a new loop for each test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    yield loop

    # Clean up
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Create a test database only once at the beginning of the test session."""
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set or empty.")

    # Drop and recreate the test database
    await _ensure_postgres_database(test_db_url, drop_if_exists=True)

    yield

    # No need to clean up the database at the end of the tests


@pytest_asyncio.fixture(autouse=True)
async def initialize_tortoise(event_loop):
    """Initialize and teardown Tortoise ORM for each test.

    This ensures each test gets a fresh database connection with the current event loop.
    """
    # Get the test database URL
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set or empty.")

    # Set up the Tortoise ORM configuration
    config = {
        "connections": {"models": test_db_url},
        "apps": {
            "models": {
                "models": ["svs_core.db.models"],
                "default_connection": "models",
            }
        },
    }

    # Initialize Tortoise with the current event loop
    await Tortoise.init(config=config)

    # Generate schemas (with safe=True to prevent errors if tables already exist)
    await Tortoise.generate_schemas(safe=True)

    # Clear all tables for a clean state
    conn = Tortoise.get_connection("models")
    for model in Tortoise.apps.get("models", {}).values():
        if hasattr(model._meta, "db_table"):
            table = model._meta.db_table
            try:
                await conn.execute_script(f'TRUNCATE TABLE "{table}" CASCADE;')
            except Exception:
                # Ignore errors during truncation
                pass

    # Proceed with the test
    yield

    # Clean up after the test
    await Tortoise.close_connections()
