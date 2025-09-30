from typing import List
from uuid import uuid4

import pytest
from docker.models.networks import Network

from svs_core.docker.network import DockerNetworkManager


class TestDockerNetworkManager:
    TEST_NETWORK_NAME = f"svs_test_network_{uuid4().hex[:8]}"

    @pytest.mark.integration
    def test_create_and_delete_network(self) -> None:
        """Tests creating and deleting a Docker network."""
        # Create a network
        network: Network = DockerNetworkManager.create_network(self.TEST_NETWORK_NAME)
        assert network.name == self.TEST_NETWORK_NAME

        # Check if the network exists
        networks: List[Network] = DockerNetworkManager.get_networks()
        assert any(n.name == self.TEST_NETWORK_NAME for n in networks)

        # Delete the network
        DockerNetworkManager.delete_network(self.TEST_NETWORK_NAME)

        # Check if the network is deleted
        networks = DockerNetworkManager.get_networks()
        assert not any(n.name == self.TEST_NETWORK_NAME for n in networks)

    @pytest.mark.integration
    def test_get_networks(self) -> None:
        """Tests retrieving a list of Docker networks."""
        networks: List[Network] = DockerNetworkManager.get_networks()
        assert isinstance(networks, list)

    @pytest.mark.integration
    def test_delete_non_existent_network(self) -> None:
        """Tests deleting a non-existent Docker network."""
        try:
            DockerNetworkManager.delete_network("non_existent_network")
        except Exception as e:
            pytest.fail(f"Deleting a non-existent network raised an exception: {e}")
