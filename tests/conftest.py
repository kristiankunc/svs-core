import asyncio
import os

import pytest
import pytest_asyncio
from pytest_mock import MockerFixture
from tortoise import Tortoise


async def _reset_test_db(db_url):
    """Reset test database - create if not exists or recreate if exists"""
    if not db_url or not db_url.startswith("postgres"):
        return

    try:
        import asyncpg

        db_name = db_url.split("/")[-1].split("?")[0]
        if not db_name:
            return

        # Connect to postgres admin DB
        admin_url = db_url.replace(f"/{db_name}", "/postgres")
        conn = await asyncpg.connect(admin_url)

        # Reset database (drop and create)
        await conn.execute(
            f"""
            SELECT pg_terminate_backend(pid) FROM pg_stat_activity
            WHERE datname = '{db_name}' AND pid <> pg_backend_pid()
        """
        )
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
        await conn.execute(f'CREATE DATABASE "{db_name}"')
        await conn.close()
    except Exception as e:
        print(f"Database setup error: {e}")


@pytest.fixture
def event_loop():
    """Create a fresh event loop for each test"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Setup test database once for the entire test session"""
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")

    await _reset_test_db(test_db_url)
    yield


@pytest_asyncio.fixture(autouse=True)
async def initialize_tortoise():
    """Initialize Tortoise ORM for each test with a clean database state"""
    test_db_url = os.environ.get("TEST_DATABASE_URL", "")
    if not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set")

    # Initialize Tortoise with minimal config
    await Tortoise.init(db_url=test_db_url, modules={"models": ["svs_core.db.models"]})
    await Tortoise.generate_schemas(safe=True)

    # Clean tables before each test
    conn = Tortoise.get_connection("default")
    for model in Tortoise.apps.get("models", {}).values():
        if hasattr(model._meta, "db_table"):
            await conn.execute_script(
                f'TRUNCATE TABLE "{model._meta.db_table}" CASCADE;'
            )

    yield
    await Tortoise.close_connections()


@pytest.fixture(autouse=True)
def mock_system_user_manager(mocker: MockerFixture) -> MockerFixture:
    """Automatically mock SystemUserManager methods to prevent actual system user creation/deletion."""
    mocker.patch(
        "svs_core.users.system.SystemUserManager.create_user",
        return_value=None,
    )
    return mocker.patch(
        "svs_core.users.system.SystemUserManager.delete_user",
        return_value=None,
    )
