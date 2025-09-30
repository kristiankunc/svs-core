import random

from svs_core.shared.shell import run_command


class SystemPortManager:
    """Class for managing system ports."""

    PORT_RANGE = range(49152, 65535)

    @staticmethod
    def is_port_used(port: int) -> bool:
        """Checks if a given port is currently in use.

        Args:
            port (int): The port number to check.

        Returns:
            bool: True if the port is in use, False otherwise.
        """
        out = run_command(f"ss -ltn | grep ':{port} '", check=False)

        return out.returncode == 0

    @staticmethod
    def find_free_port() -> int:
        """Finds a free port within the defined PORT_RANGE.

        Tries up to MAX_ATTEMPTS times to find a free port.

        Returns:
            int: A free port number if available.

        Raises:
            RuntimeError: If no free port is found within the maximum attempts.
        """
        MAX_ATTEMPTS = 50
        attempts = 0

        while attempts < MAX_ATTEMPTS:

            port = random.choice(SystemPortManager.PORT_RANGE)
            if not SystemPortManager.is_port_used(port):
                return port

            attempts += 1

        raise RuntimeError("No free port found")
