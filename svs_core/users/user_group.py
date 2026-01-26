from typing import cast

from svs_core.db.models import UserGroupModel
from svs_core.shared.exceptions import AlreadyExistsException
from svs_core.shared.logger import get_logger
from svs_core.users.user import User


class UserGroup(UserGroupModel):
    """User class representing a user group in the system."""

    class Meta:  # noqa: D106
        proxy = True

    @classmethod
    def create(cls, name: str, description: str | None = None) -> "UserGroup":
        """Creates a new user group with the given name.

        Args:
            name (str): The name for the new user group.
            description (str | None): The description for the new user group.

        Raises:
            AlreadyExistsException: If the user group name already exists.

        Returns:
            UserGroup: The created user group.
        """
        if cls.objects.filter(name=name).exists():
            raise AlreadyExistsException("user group", name)
        user_group = cls.objects.create(name=name, description=description)
        get_logger(__name__).info(f"Created user group '{name}'")

        return cast(UserGroup, user_group)

    def add_member(self, user: "User") -> None:
        """Adds a user to the user group.

        Args:
            user (User): The user to add to the group.
        """
        self.members.add(user)
        self.save()
        get_logger(__name__).info(f"Added user '{user.name}' to group '{self.name}'")

    def remove_member(self, user: "User") -> None:
        """Removes a user from the user group.

        Args:
            user (User): The user to remove from the group.
        """
        self.members.remove(user)
        self.save()
        get_logger(__name__).info(
            f"Removed user '{user.name}' from group '{self.name}'"
        )
