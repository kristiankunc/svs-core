import os

import pytest
from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    db_url = os.environ.get("TEST_DATABASE_URL")
    if not db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set or empty.")

    os.environ["PGDATABASE"] = "devdb"  # TODO: grab this directly from the environment

    print(f"Using database URL: {db_url}")

    initializer(["svs_core.db.models"], db_url=db_url, app_label="models")

    request.addfinalizer(finalizer)
