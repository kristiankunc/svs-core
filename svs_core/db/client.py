import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

engine = create_engine(os.getenv("DATABASE_URL", ""), echo=True)

SessionLocal = sessionmaker(bind=engine)


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Provides a transactional scope around a series of operations.
    This function is a context manager that creates a new database session
    for each operation. It ensures that the session is committed if the
    operation is successful, or rolled back if an error occurs.

    Example:
    ```python
    with get_db_session() as session:
        # Perform database operations
        user = session.query(User).filter_by(id=1).first()
        print(user.name)
        # The session is automatically committed or rolled back
    ```
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()
