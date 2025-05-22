import pytest
from typing import Generator
from sqlalchemy.orm import Session


class DBTestBase:
    @pytest.fixture(autouse=True)
    def _inject_session(self, db_session: Generator[Session, None, None]) -> None:
        self.db = db_session
