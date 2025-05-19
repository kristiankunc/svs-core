import logging
from svs_core.event_adapters.base import Adapter
from svs_core.shared.logger import get_logger
from svs_core.shared.shell import run_command


class SystemAdapter(Adapter):
    def create_user(self, username: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Creating user {username}")

        run_command(f"sudo useradd -m {username}")
        run_command(f"sudo chmod 400 /home/{username}/.ssh/authorized_keys")

        get_logger(__name__).log(logging.INFO, f"User {username} created")

    def delete_user(self, username: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Deleting user {username}")

        run_command(f"sudo userdel -r {username}")

        get_logger(__name__).log(logging.INFO, f"User {username} deleted")

    def add_ssh_key(self, username: str, ssh_key: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Adding SSH key for user {username}")

        run_command(f"sudo mkdir -p /home/{username}/.ssh")
        run_command(
            f"echo '{ssh_key}' | sudo tee -a /home/{username}/.ssh/authorized_keys")
        run_command(
            f"sudo chown {username}:{username} /home/{username}/.ssh/authorized_keys")
        run_command(f"sudo chmod 400 /home/{username}/.ssh/authorized_keys")

        get_logger(__name__).log(logging.INFO, f"SSH key added for user {username}")

    def delete_ssh_key(self, username: str, ssh_key: str) -> None:
        get_logger(__name__).log(logging.INFO, f"Deleting SSH key for user {username}")

        run_command(f"sudo sed -i '/{ssh_key}/d' /home/{username}/.ssh/authorized_keys")

        get_logger(__name__).log(logging.INFO, f"SSH key deleted for user {username}")
