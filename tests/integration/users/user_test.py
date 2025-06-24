# tests/test_user.py

import pytest
from tortoise.contrib.test import TestCase

from svs_core.users.user import User


class TestUser(TestCase):
    @pytest.mark.integration
    async def test_create_and_get_user(self):
        created_user = await User.create(name="Alice", password="supersecret")
        fetched_user = await User.get_by_name("Alice")

        assert fetched_user is not None
        assert (
            fetched_user.name == created_user.name
            and fetched_user.id == created_user.id
        )
