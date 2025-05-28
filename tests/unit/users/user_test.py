from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from svs_core.db.models import UserModel
from svs_core.users.user import User


class TestUser:
    @pytest.mark.unit
    def test_user_from_orm(self) -> None:
        """Test User creation from an ORM model."""

        mock_user_model: MagicMock = MagicMock(spec=UserModel)
        mock_user_model.id = 1
        mock_user_model.name = "orm_user"

        user: User = User.from_orm(mock_user_model)

        assert user.id == mock_user_model.id
        assert isinstance(user.id, int)
        assert user.name == mock_user_model.name
        assert isinstance(user.name, str)

    @pytest.mark.unit
    @patch("svs_core.users.user.DockerNetworkManager.delete_network")
    @patch("svs_core.db.client.DBClient.delete_user")
    def test_user_delete_self(
        self, mock_delete_user: MagicMock, mock_delete_network: MagicMock
    ) -> None:
        """Test the delete_self method."""

        user_id: int = 1
        user_name: str = "test_user_to_delete"
        user: User = User(
            id=user_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            name=user_name,
            _orm_check=True,
        )

        user.delete_self()

        mock_delete_user.assert_called_once_with(user_id)
        mock_delete_network.assert_called_once_with(user_name)
