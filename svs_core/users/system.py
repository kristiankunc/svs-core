from svs_core.shared.shell import run_command


class SystemUserManager:
    @staticmethod
    def create_user(username: str, password: str, admin: bool = False) -> None:
        # Create user
        run_command(f"sudo useradd -m {username}", check=True)
        run_command(f"echo '{username}:{password}' | sudo chpasswd", check=True)
        run_command(f"sudo usermod -aG svs-users {username}", check=True)

        if admin:
            run_command(f"sudo usermod -aG svs-admins {username}", check=True)

    @staticmethod
    def delete_user(username: str) -> None:
        run_command(f"sudo userdel -r {username}", check=True)
