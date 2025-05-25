import pytest
from sqlalchemy.orm import Session
from typing import Optional

from svs_core.db.client import DBClient
from svs_core.users.user import User
from svs_core.db.models import UserModel


class TestDBClient:
    @pytest.mark.integration
    def test_create_and_get_user(self, db_session: Session) -> None:
        """
        Tests creating a user and then retrieving them by name.
        """
        username: str = "test_user_create_get"
        created_user: User = DBClient.create_user(username=username)

        assert created_user is not None
        assert created_user.name == username
        assert isinstance(created_user.id, int)

        retrieved_user: Optional[User] = DBClient.get_user_by_name(username=username)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.name == username

    @pytest.mark.integration
    def test_get_user_by_name_non_existent(self, db_session: Session) -> None:
        """
        Tests retrieving a non-existent user by name.
        """
        username: str = "non_existent_user"
        retrieved_user: Optional[User] = DBClient.get_user_by_name(username=username)
        assert retrieved_user is None

    @pytest.mark.integration
    def test_delete_user(self, db_session: Session) -> None:
        """
        Tests deleting a user.
        """
        username: str = "test_user_delete"
        user_model = UserModel(name=username)
        db_session.add(user_model)
        db_session.commit()

        user_id: int = user_model.id
        db_session.expunge(user_model)

        fetched_model_before_delete = (
            db_session.query(UserModel).filter_by(id=user_id).first()
        )

        assert fetched_model_before_delete is not None
        assert fetched_model_before_delete.name == username

        DBClient.delete_user(user_id=user_id)

        # Verify the user is deleted using a new session
        with DBClient.get_db_session() as verify_session:
            deleted_user_model = (
                verify_session.query(UserModel).filter_by(id=user_id).first()
            )
            assert deleted_user_model is None

        # Verify get_user_by_name also returns None
        retrieved_user_after_delete: Optional[User] = DBClient.get_user_by_name(
            username=username
        )
        assert retrieved_user_after_delete is None

    @pytest.mark.integration
    def test_delete_non_existent_user(self, db_session: Session) -> None:
        """
        Tests deleting a non-existent user.
        """
        non_existent_user_id: int = 99999
        # This should not raise an error, just do nothing
        DBClient.delete_user(user_id=non_existent_user_id)

        # Verify no user with this ID exists
        deleted_user_model = (
            db_session.query(UserModel).filter_by(id=non_existent_user_id).first()
        )
        assert deleted_user_model is None
