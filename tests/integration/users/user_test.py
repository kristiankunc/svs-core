# tests/test_user.py

import pytest
from tortoise.contrib.test import TestCase

from svs_core.users.user import User


class TestUser(TestCase):
    @pytest.mark.integration
    async def test_create_and_get_user(self):
        await User.create(
            name="Alice", email="alice@example.com", password="supersecret"
        )
        fetched_user = await User.get_by_email("alice@example.com")

        assert fetched_user is not None
        assert fetched_user.email == "alice@example.com"
