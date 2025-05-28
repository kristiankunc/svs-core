import os
from contextlib import contextmanager
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

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
        Provides a session scope around a series of operations.
        This function is a context manager that creates a new database session
        for each operation. It doesn't automatically commit - the consumer must
        explicitly call session.commit() when ready.

        Example:
        ```python
        with DBClient.get_db_session() as session:
            # Perform database operations
            user = session.query(User).filter_by(id=1).first()
            print(user.name)
            # Call session.commit() explicitly if needed
            session.commit()
        ```
        """
        session = SessionLocal()
        try:
            yield session
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
                created_at=model.created_at,
                updated_at=model.updated_at,
                name=model.name,
                _orm_check=True,
            )
            return user

    @staticmethod
    def create_user(username: str) -> User:
        """
        Creates a new user in the database.

        Args:
            username (str): The username to create.

        Raises:
            ValueError: If the username is invalid.
        """
        with DBClient.get_db_session() as session:
            user_model = UserModel.create(
                name=username,
            )
            session.add(user_model)
            session.flush()
            session.refresh(user_model)
            created_user = User.from_orm(user_model, _orm_check=True)
            session.commit()

        return created_user

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
                session.commit()
