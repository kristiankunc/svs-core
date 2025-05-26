import docker
from docker.models.networks import Network
from typing import List
from docker.errors import NotFound


class DockerNetworkManager:
    @staticmethod
    def _get_client() -> docker.DockerClient:
        """
        Returns a Docker client instance.

        Returns:
            docker.DockerClient: A Docker client instance.
        """
        return docker.from_env()

    @staticmethod
    def get_networks() -> List[Network]:
        """
        Retrieves a list of Docker networks.

        Returns:
            list[Network]: A list of Docker network objects.
        """

        client = DockerNetworkManager._get_client()
        return client.networks.list()  # type: ignore

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

        client = DockerNetworkManager._get_client()

        return client.networks.create(name=name)

    @staticmethod
    def delete_network(name: str) -> None:
        """
        Deletes a Docker network by its name.

        Args:
            name (str): The name of the network to delete.

        Raises:
            docker.errors.APIError: If the network deletion fails.
        """

        client = DockerNetworkManager._get_client()
        try:
            network = client.networks.get(name)
            network.remove()
        except NotFound:
            pass
