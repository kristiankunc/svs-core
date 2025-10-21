from typing import Any, List

from docker.errors import NotFound
from docker.models.networks import Network

from svs_core.docker.base import get_docker_client
from svs_core.shared.logger import get_logger


class DockerNetworkManager:
    """Class for managing Docker networks."""

    @staticmethod
    def get_networks() -> List[Network]:
        """Retrieves a list of Docker networks.

        Returns:
            list[Network]: A list of Docker network objects.
        """
        return get_docker_client().networks.list()  # type: ignore

    @staticmethod
    def get_network(name: str) -> Network | None:
        """Retrieves a Docker network by its name.

        Args:
            name (str): The name of the network to retrieve.

        Returns:
            Network | None: The Docker network object if found, otherwise None.
        """
        try:
            return get_docker_client().networks.get(name)
        except NotFound:
            return None

    @staticmethod
    def create_network(name: str, labels: dict[str, Any] | None = None) -> Network:
        """Creates a new Docker network.

        Args:
            name (str): The name of the network to create.

        Returns:
            Network: The created Docker network object.

        Raises:
            docker.errors.APIError: If the network creation fails.
        """
        get_logger(__name__).debug(
            f"Creating network with name: {name} and labels: {labels}"
        )

        return get_docker_client().networks.create(name=name, labels=labels)

    @staticmethod
    def delete_network(name: str) -> None:
        """Deletes a Docker network by its name.

        Args:
            name (str): The name of the network to delete.

        Raises:
            docker.errors.APIError: If the network deletion fails.
        """
        get_logger(__name__).debug(f"Deleting network with name: {name}")

        try:
            network = get_docker_client().networks.get(name)
            network.remove()
        except NotFound:
            pass
