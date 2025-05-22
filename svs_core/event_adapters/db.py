import logging
from typing import TYPE_CHECKING
from svs_core.db.client import get_db_session
from svs_core.db.models import UserModel
from svs_core.db.models import SSHKeyModel
from svs_core.shared.logger import get_logger

if TYPE_CHECKING:
    from svs_core.users.user import User
    from svs_core.users.ssh_key import SSHKey


class DBAdapter:
    """
    DBAdapter is an effect adapter that interacts with the database to perform operations
    """

    def _construct_user(self, user_model: UserModel) -> "User":
        """Constructs a User object from a UserModel.

        Args:
            user_model (UserModel): The user model to construct the user from.

        Returns:
            User: The constructed user object.
        """

        from svs_core.users.user import User

        return User.from_orm(user_model)

    @staticmethod
    def create_user(username: str) -> "User":
        """Creates a new user in the database.

        Args:
            username (str): The username to create.

        Returns:
            User: The created user object.
        """
        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        with get_db_session() as session:
            user_model = UserModel.create(username)
            session.add(user_model)

        get_logger(__name__).log(logging.INFO, f"User {username} created")

        return User.from_orm(user_model)

    @staticmethod
    def delete_user(user: "User") -> None:
        """Deletes a user from the database.
        Args:
            user (User): The user to delete.

        Raises:
            ValueError: If the user is not found in the database. # TODO: remove this, safely assume everything is ok
        """

        get_logger(__name__).log(logging.INFO, f"Deleting user {user.name}")

        with get_db_session() as session:
            model = session.query(UserModel).filter_by(name=user.name).first()
            if model:
                session.delete(user)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"User {user.name} not found, cannot delete"
                )
                raise ValueError(f"User {user.name} not found")

        get_logger(__name__).log(logging.INFO, f"User {user.name} deleted")

    @staticmethod
    def add_ssh_key(user: "User", key_name: str, key_content: str) -> "SSHKey":
        """Adds an SSH key to the user's authorized keys in the database.

        Args:
            user (User): The user to add the SSH key for.
            key_name (str): The name of the SSH key.
            key_content (str): The content of the SSH key (public key).

        Returns:
            SSHKey: The created SSH key object.

        Raises:
            ValueError: If the user is not found in the database. # TODO: remove this, safely assume everything is ok
        """
        get_logger(__name__).log(logging.INFO, f"Adding SSH key for user {user.name}")

        with get_db_session() as session:
            key_user = session.query(UserModel).filter_by(name=user.name).first()
            if not key_user:
                get_logger(__name__).log(
                    logging.WARNING, f"User {user.name} not found, cannot add SSH key"
                )
                raise ValueError(f"User {user.name} not found")

            key_model = SSHKeyModel.create(
                name=key_name,
                content=key_content,
                user_id=key_user.id,
            )

        get_logger(__name__).log(logging.INFO, f"SSH key added for user {user.name}")

        return SSHKey.from_orm(key_model)

    @staticmethod
    def delete_ssh_key(user: "User", ssh_key: "SSHKey") -> None:
        """Deletes an SSH key from the user's authorized keys in the database.

        Args:
            user (User): The user to delete the SSH key for.
            ssh_key (SSHKey): The SSH key to delete.

        Raises:
            ValueError: If the SSH key is not found in the database.
        """

        get_logger(__name__).log(logging.INFO, f"Deleting SSH key for user {user.name}")

        with get_db_session() as session:
            key_model = session.query(SSHKeyModel).filter_by(id=ssh_key.id).first()
            if key_model:
                session.delete(key_model)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"SSH key {ssh_key.name} not found, cannot delete"
                )
                raise ValueError(f"SSH key {ssh_key.name} not found")

        get_logger(__name__).log(logging.INFO, f"SSH key deleted for user {user.name}")
