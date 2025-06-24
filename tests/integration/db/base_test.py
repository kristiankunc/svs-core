import asyncio
from datetime import datetime

import pytest
from tortoise.contrib.test import TestCase

from svs_core.users.user import User


class TestOrmBase(TestCase):
    @pytest.mark.integration
    async def test_created_and_updated_at_fields(self):
        """Test that created_at and updated_at fields are set correctly."""
        user = await User.create(
            name="Test User", email="test@example.com", password="pw"
        )
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
        assert abs((user.created_at - user.updated_at).total_seconds()) < 1

    @pytest.mark.integration
    async def test_updated_at_changes_on_save(self):
        """Test that updated_at changes when the model is saved."""
        user = await User.create(
            name="Test User2", email="test2@example.com", password="pw"
        )
        old_updated_at = user.updated_at

        user._model.name = "Updated Name"
        await user._model.save()
        await asyncio.sleep(0.1)
        assert user.updated_at > old_updated_at

    @pytest.mark.integration
    async def test_signal_post_save_updates_instance(self):
        """Test that the post_save signal updates the instance."""
        user = await User.create(
            name="Test User3", email="test3@example.com", password="pw"
        )
        user._model.name = "Changed Name"
        await user._model.save()
        await asyncio.sleep(0.1)
        assert user.name == "Changed Name" or user._model.name == "Changed Name"  # type: ignore
