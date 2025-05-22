import pytest
import subprocess
from sqlalchemy.orm import Session
from typing import Generator

from svs_core.db.client import SessionLocal


def pytest_sessionstart() -> None:
    """This will install the package in editable mode before any tests are run."""
    subprocess.run(["pip", "install", "-e", "."], check=True)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy session wrapped in a rollback-based transaction.
    The session is rolled back after the test to keep DB clean.

    Returns:
        Generator[Session, None, None]: A generator that yields a SQLAlchemy session.
    """

    session: Session = SessionLocal()
    trans = session.begin()
    try:
        yield session
        trans.rollback()
    finally:
        session.close()
