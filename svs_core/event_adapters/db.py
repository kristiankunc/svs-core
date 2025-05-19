import logging
from svs_core.event_adapters.base import Adapter
from svs_core.db.client import get_db_session
from svs_core.db.models import User
from svs_core.shared.logger import get_logger


class DBAdapter(Adapter):
    def create_user(self, username: str):
        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        with get_db_session() as session:
            user = User.create(username)
            session.add(user)

        get_logger(__name__).log(logging.INFO, f"User {username} created")

    def delete_user(self, *args, **kwargs):
        get_logger(__name__).log(logging.INFO, f"Deleting user {args[0]}")

        with get_db_session() as session:
            user = session.query(User).filter_by(name=args[0]).first()
            if user:
                session.delete(user)
            else:
                get_logger(__name__).log(
                    logging.WARNING, f"User {args[0]} not found in DB")

        get_logger(__name__).log(logging.INFO, f"User {args[0]} deleted")

    def add_ssh_key(self, *args, **kwargs): pass
    def delete_ssh_key(self, *args, **kwargs): pass
