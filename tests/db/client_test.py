import pytest
from pytest_mock import MockerFixture
from svs_core.db import client
import os


@pytest.fixture(autouse=True)  # type: ignore
def mock_database_url(mocker: MockerFixture) -> None:
    """Mock DATABASE_URL environment variable."""
    mocker.patch.dict(os.environ, {"DATABASE_URL": "sqlite:///test.db"})


@pytest.fixture(autouse=True)  # type: ignore
def mock_sqlite(mocker: MockerFixture) -> None:
    """Mock SQLite engine and connection."""
    mocker.patch("sqlalchemy.create_engine")


def test_get_db_session_commits_on_success(mocker: MockerFixture) -> None:
    """Test that the session commits on success."""

    mock_session = mocker.MagicMock()
    mocker.patch.object(client, "SessionLocal", return_value=mock_session)

    with client.get_db_session() as session:
        assert session is mock_session
        session.query.return_value.all.return_value = ["result"]  # type: ignore
        assert session.query().all() == ["result"]

    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    mock_session.close.assert_called_once()


def test_get_db_session_rolls_back_on_exception(mocker: MockerFixture) -> None:
    """Test that the session rolls back on exception."""

    mock_session = mocker.MagicMock()
    mocker.patch.object(client, "SessionLocal", return_value=mock_session)

    with pytest.raises(ValueError):
        with client.get_db_session():
            raise ValueError("fail")

    mock_session.commit.assert_not_called()
    mock_session.rollback.assert_called_once()
    mock_session.close.assert_called_once()


def test_get_db_session_closes_on_exit(mocker: MockerFixture) -> None:
    """Test that the session closes on exit."""

    mock_session = mocker.MagicMock()
    mocker.patch.object(client, "SessionLocal", return_value=mock_session)

    try:
        with client.get_db_session():
            pass
    except Exception:
        pass

    mock_session.close.assert_called_once()
