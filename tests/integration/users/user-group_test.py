import pytest

from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.users.user import User
from svs_core.users.user_group import UserGroup


class TestUserGroupIntegration:
    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_group_success(self):
        name = "testgroup"
        description = "A test group"

        group = UserGroup.create(name=name, description=description)

        assert group.name == name
        assert group.description == description
        assert UserGroup.objects.get(name=name) is not None

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_user_group_duplicate(self):
        name = "dupegroup"
        UserGroup.create(name=name)
        with pytest.raises(AlreadyExistsException):
            UserGroup.create(name=name)

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_add_and_remove_member(self, test_user):
        # Create a group and add a user as member, then remove them
        group = UserGroup.create(name="membership-group")

        # Initially no members
        assert group.members.count() == 0

        # Add member
        group.add_member(test_user)
        # Reload from DB to ensure relationship persisted
        refreshed = UserGroup.objects.get(id=group.id)
        assert refreshed.members.count() == 1
        assert refreshed.members.filter(id=test_user.id).exists()

        # Remove member
        refreshed.remove_member(test_user)
        refreshed_after = UserGroup.objects.get(id=group.id)
        assert refreshed_after.members.count() == 0
