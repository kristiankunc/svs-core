from svs_core.shared.shell import run_command


class SystemUserManager:
    @staticmethod
    def create_user(username: str, password: str) -> None:
        # Create user
        run_command(f"sudo useradd -m {username}", check=True)
        run_command(f"echo '{username}:{password}' | sudo chpasswd", check=True)

    @staticmethod
    def delete_user(username: str) -> None:
        run_command(f"sudo userdel -r {username}", check=True)
