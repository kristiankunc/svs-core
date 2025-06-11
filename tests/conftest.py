import subprocess


def pytest_sessionstart() -> None:
    """This will install the package in editable mode before any tests are run."""
    subprocess.run(["pip", "install", "-e", "."], check=True)


"""
@pytest.fixture(scope="function")
def setup_db() -> None:
    Fixture that sets up the database before tests run.

    It drops all tables in the database and recreates the ones defined in the models.

    from svs_core.db.client import engine
    from svs_core.db.models import Base

    inspector = inspect(engine)
    print(f"Using database URL: {engine.url}")

    with engine.begin() as conn:
        table_names = inspector.get_table_names()

        for table_name in table_names:
            conn.execute(text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE'))

    Base.metadata.create_all(engine)


@pytest.fixture(scope="function")
def db_session(setup_db: None) -> Generator[Session, None, None]:
    Fixture that provides a database session for tests.

    This fixture is used to ensure that each test has a clean database session.
    It is scoped to the function level, meaning it will be created and destroyed
    for each test function.

    Yields:
        Session: A SQLAlchemy session object for database operations.

    from svs_core.db.client import DBClient

    with DBClient.get_db_session() as session:
        yield session
"""
