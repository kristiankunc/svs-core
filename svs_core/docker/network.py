from typing import List

from docker.errors import NotFound
from docker.models.networks import Network

from svs_core.docker.base import get_docker_client


class DockerNetworkManager:
    @staticmethod
    def get_networks() -> List[Network]:
        """
        Retrieves a list of Docker networks.

        Returns:
            list[Network]: A list of Docker network objects.
        """

        return get_docker_client().networks.list()  # type: ignore

    @staticmethod
    def create_network(name: str) -> Network:
        """
        Creates a new Docker network.

        Args:
            name (str): The name of the network to create.

        Returns:
            Network: The created Docker network object.

        Raises:
            docker.errors.APIError: If the network creation fails.
        """

        return get_docker_client().networks.create(name=name)

    @staticmethod
    def delete_network(name: str) -> None:
        """
        Deletes a Docker network by its name.

        Args:
            name (str): The name of the network to delete.

        Raises:
            docker.errors.APIError: If the network deletion fails.
        """

        try:
            network = get_docker_client().networks.get(name)
            network.remove()
        except NotFound:
            pass
