import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator, Optional

from svs_core.db.models import UserModel
from svs_core.users.user import User

DATABASE_URL = os.environ.get("DATABASE_URL")
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

url = TEST_DATABASE_URL if "PYTEST_CURRENT_TEST" in os.environ else DATABASE_URL

if not url:
    raise ValueError("DATABASE_URL or TEST_DATABASE_URL environment variable not set.")

engine = create_engine(url, future=True)
SessionLocal = sessionmaker(bind=engine)


class DBClient:
    @staticmethod
    @contextmanager
    def get_db_session() -> Generator[Session, None, None]:
        """
        Provides a transactional scope around a series of operations.
        This function is a context manager that creates a new database session
        for each operation. It ensures that the session is committed if the
        operation is successful, or rolled back if an error occurs.

        Example:
        ```python
        with DBClient.get_db_session() as session:
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

    @staticmethod
    def get_user_by_name(username: str) -> Optional[User]:
        """
        Retrieves a user by their username from the database.

        Args:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object if found, otherwise raises an exception.
        """

        with DBClient.get_db_session() as session:
            model = session.query(UserModel).filter_by(name=username).first()
        if not model:
            return None

        user = User(
            id=model.id,
            name=model.name,
            _orm_check=True,
        )
        return user

    @staticmethod
    def creare_user(username: str) -> User:
        """
        Creates a new user in the database.

        Args:
            username (str): The username to create.

        Raises:
            ValueError: If the username is invalid.
        """

        with DBClient.get_db_session() as session:
            user = UserModel(name=username)
            session.add(user)

        return User(
            id=user.id,
            name=user.name,
            _orm_check=True,
        )

    @staticmethod
    def delete_user(user_id: int) -> None:
        """
        Deletes a user from the database by their ID.

        Args:
            user_id (int): The ID of the user to delete.
        """

        with DBClient.get_db_session() as session:
            user = session.query(UserModel).filter_by(id=user_id).first()
            if user:
                session.delete(user)
