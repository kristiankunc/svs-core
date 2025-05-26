from typing import List

import pytest
from docker.models.networks import Network

from svs_core.docker.network import DockerNetworkManager

TEST_NETWORK_NAME = "test_network"


# Removed the network_manager fixture as it's not needed for static methods


@pytest.mark.integration
def test_create_and_delete_network() -> None:
    """
    Tests creating and deleting a Docker network.
    """
    # Create a network
    network: Network = DockerNetworkManager.create_network(TEST_NETWORK_NAME)
    assert network.name == TEST_NETWORK_NAME

    # Check if the network exists
    networks: List[Network] = DockerNetworkManager.get_networks()
    assert any(n.name == TEST_NETWORK_NAME for n in networks)

    # Delete the network
    DockerNetworkManager.delete_network(TEST_NETWORK_NAME)

    # Check if the network is deleted
    networks = DockerNetworkManager.get_networks()
    assert not any(n.name == TEST_NETWORK_NAME for n in networks)


@pytest.mark.integration
def test_get_networks() -> None:
    """
    Tests retrieving a list of Docker networks.
    """
    networks: List[Network] = DockerNetworkManager.get_networks()
    assert isinstance(networks, list)


@pytest.mark.integration
def test_delete_non_existent_network() -> None:
    """
    Tests deleting a non-existent Docker network.
    It should not raise an error.
    """
    try:
        DockerNetworkManager.delete_network("non_existent_network")
    except Exception as e:
        pytest.fail(f"Deleting a non-existent network raised an exception: {e}")
