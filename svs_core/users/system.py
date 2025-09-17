from svs_core.shared.shell import run_command


class SystemUserManager:
    @staticmethod
    def create_user(username: str, password: str, admin: bool = False) -> None:
        """
        Creates a system user with the given username and password.

        Args:
            username (str): The username for the new system user.
            password (str): The password for the new system user.
            admin (bool, optional): Whether to add the user to the admin group. Defaults to False.
        """

        run_command(f"sudo useradd -m {username}", check=True)
        run_command(f"echo '{username}:{password}' | sudo chpasswd", check=True)
        run_command(f"sudo usermod -aG svs-users {username}", check=True)

        if admin:
            run_command(f"sudo usermod -aG svs-admins {username}", check=True)

    @staticmethod
    def delete_user(username: str) -> None:
        """
        Deletes the system user with the given username.
        Args:
            username (str): The username of the system user to delete.
        """
        run_command(f"sudo userdel -r {username}", check=True)
