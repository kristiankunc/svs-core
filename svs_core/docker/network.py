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
        get_logger(__name__).debug(f"Retrieving network '{name}'")

        try:
            network = get_docker_client().networks.get(name)
            get_logger(__name__).debug(f"Network '{name}' found")
            return network
        except NotFound:
            get_logger(__name__).debug(f"Network '{name}' not found")
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
        get_logger(__name__).info(f"Creating Docker network '{name}'")
        get_logger(__name__).debug(f"Network labels: {labels}")

        try:
            network = get_docker_client().networks.create(name=name, labels=labels)
            get_logger(__name__).info(f"Successfully created network '{name}'")
            return network
        except Exception as e:
            get_logger(__name__).error(f"Failed to create network '{name}': {str(e)}")
            raise

    @staticmethod
    def delete_network(name: str) -> None:
        """Deletes a Docker network by its name.

        Args:
            name (str): The name of the network to delete.

        Raises:
            docker.errors.APIError: If the network deletion fails.
        """
        get_logger(__name__).info(f"Deleting Docker network '{name}'")

        try:
            network = get_docker_client().networks.get(name)
            network.remove()
            get_logger(__name__).info(f"Successfully deleted network '{name}'")
        except NotFound:
            get_logger(__name__).debug(f"Network '{name}' not found, nothing to delete")
        except Exception as e:
            get_logger(__name__).error(f"Failed to delete network '{name}': {str(e)}")
            raise
