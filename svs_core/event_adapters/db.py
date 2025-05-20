import logging
from svs_core.db.client import get_db_session
from svs_core.db.models import UserModel
from svs_core.db.models import SSHKeyModel
from svs_core.users.user import User
from svs_core.users.ssh_key import SSHKey
from svs_core.shared.logger import get_logger

class DBAdapter():
    @staticmethod
    def create_user(username: str) -> User:
        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        with get_db_session() as session:
            user_model = UserModel.create(username)
            session.add(user_model)

        get_logger(__name__).log(logging.INFO, f"User {username} created")

        return User.from_orm(user_model)
    
    @staticmethod
    def delete_user(user: User) -> None:
        get_logger(__name__).log(logging.INFO, f"Deleting user {user.name}")

        with get_db_session() as session:
            model = session.query(UserModel).filter_by(name=user.name).first()
            if model:
                session.delete(user)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"User {user.name} not found, cannot delete")
                raise ValueError(f"User {user.name} not found")

        get_logger(__name__).log(logging.INFO, f"User {user.name} deleted")

    @staticmethod
    def add_ssh_key(user: User, key_name: str, key_content: str) -> SSHKey:
        get_logger(__name__).log(logging.INFO, f"Adding SSH key for user {user.name}")

        with get_db_session() as session:
            key_user = session.query(UserModel).filter_by(name=user.name).first()
            if not key_user:
                get_logger(__name__).log(
                    logging.WARNING, f"User {user.name} not found, cannot add SSH key")
                raise ValueError(f"User {user.name} not found")

            key_model = SSHKeyModel.create(
                name=key_name,
                content=key_content,
                user_id=key_user.id,
            )

        get_logger(__name__).log(logging.INFO, f"SSH key added for user {user.name}")

        return SSHKey.from_orm(key_model)

    @staticmethod
    def delete_ssh_key(user: User, ssh_key: SSHKey) -> None:
        get_logger(__name__).log(logging.INFO, f"Deleting SSH key for user {user.name}")

        with get_db_session() as session:
            key_model = session.query(SSHKeyModel).filter_by(id=ssh_key.id).first()
            if key_model:
                session.delete(key_model)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"SSH key {ssh_key.name} not found, cannot delete")
                raise ValueError(f"SSH key {ssh_key.name} not found")

        get_logger(__name__).log(logging.INFO, f"SSH key deleted for user {user.name}")
