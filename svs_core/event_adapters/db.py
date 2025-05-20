import logging
from svs_core.event_adapters.base import Adapter
from svs_core.db.client import get_db_session
from svs_core.db.models import User
from svs_core.shared.logger import get_logger


class DBAdapter(Adapter):
    def create_user(self, username: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        with get_db_session() as session:
            user = User.create(username)
            session.add(user)

        get_logger(__name__).log(logging.INFO, f"User {username} created")

    def delete_user(self, username: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Deleting user {username}")

        with get_db_session() as session:
            user = session.query(User).filter_by(name=username).first()
            if user:
                session.delete(user)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"User {username} not found, cannot delete")

        get_logger(__name__).log(logging.INFO, f"User {username} deleted")

    def add_ssh_key(self, username: str, ssh_key: str) -> None: pass

    def delete_ssh_key(self, username: str, ssh_key: str) -> None: pass
