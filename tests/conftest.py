import os

import pytest
from tortoise.contrib.test import finalizer, initializer


@pytest.fixture(scope="session", autouse=True)
def initialize_tests(request):
    test_db_url = os.environ.get("TEST_DATABASE_URL")
    db_url = os.environ.get("DATABASE_URL")

    if not db_url or not test_db_url:
        raise ValueError("TEST_DATABASE_URL environment variable is not set or empty.")

    os.environ["PGDATABASE"] = db_url.split("/")[-1]

    initializer(["svs_core.db.models"], db_url=test_db_url, app_label="models")

    request.addfinalizer(finalizer)
