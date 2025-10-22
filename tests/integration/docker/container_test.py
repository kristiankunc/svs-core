import uuid

import pytest

from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import Label


class TestDockerContainerManager:
    """Integration tests for the DockerContainerManager class."""

    TEST_IMAGE = "alpine:latest"
    TEST_CONTAINER_NAME = f"svs-test-container-{str(uuid.uuid4())[:8]}"

    @pytest.fixture(scope="session", autouse=True)
    def pull_test_image(self):
        """Fixture to pull the test image before all tests."""
        if not DockerImageManager.exists(
            self.TEST_IMAGE.split(":")[0], self.TEST_IMAGE.split(":")[1]
        ):
            DockerImageManager.pull(
                self.TEST_IMAGE.split(":")[0], self.TEST_IMAGE.split(":")[1]
            )

    @pytest.fixture(autouse=True)
    def cleanup_test_containers(self):
        """Fixture to clean up test containers before and after tests."""
        self.cleanup_container()

        yield

        self.cleanup_container()

    def cleanup_container(self) -> None:
        """Helper method to clean up test container if it exists."""
        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        if container:
            DockerContainerManager.remove(self.TEST_CONTAINER_NAME)

    @pytest.mark.integration
    def test_create_container(self) -> None:
        """Test creating a Docker container."""
        # Create a container
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
        )

        assert container is not None
        assert container.name == self.TEST_CONTAINER_NAME

        fetched_container = DockerContainerManager.get_container(
            self.TEST_CONTAINER_NAME
        )
        assert fetched_container is not None

    @pytest.mark.integration
    def test_create_container_with_command(self) -> None:
        """Test creating a Docker container with a command."""
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            command="echo",
            args=["Hello, Docker!"],
        )

        assert container is not None

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status in ["running", "exited", "created"]

    @pytest.mark.integration
    def test_create_container_with_labels(self) -> None:
        """Test creating a Docker container with labels."""
        labels = [
            Label(key="com.svs.test1", value="value1"),
            Label(key="com.svs.test2", value="value2"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME, image=self.TEST_IMAGE, labels=labels
        )

        assert container is not None

        container_labels = container.labels
        assert container_labels.get("com.svs.test1") == "value1"
        assert container_labels.get("com.svs.test2") == "value2"

    @pytest.mark.integration
    def test_create_container_with_ports(self) -> None:
        """Test creating a Docker container with port mappings."""
        ports = {"80/tcp": 49152}

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            command="tail",
            args=["-f", "/dev/null"],
            ports=ports,
        )

        assert container is not None

        DockerContainerManager.start_container(container)
        container.reload()

        assert container.status == "running"

    @pytest.mark.integration
    def test_get_container(self) -> None:
        """Test getting a Docker container by ID."""
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
        )

        fetched_container = DockerContainerManager.get_container(
            self.TEST_CONTAINER_NAME
        )

        assert fetched_container is not None
        assert fetched_container.id == container.id

    @pytest.mark.integration
    def test_get_container_nonexistent(self) -> None:
        """Test getting a nonexistent Docker container."""
        container = DockerContainerManager.get_container(f"nonexistent-{uuid.uuid4()}")

        assert container is None

    @pytest.mark.integration
    def test_get_all(self) -> None:
        """Test getting all Docker containers."""
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
        )

        containers = DockerContainerManager.get_all()

        assert isinstance(containers, list)
        container_names = [container.name for container in containers]
        assert self.TEST_CONTAINER_NAME in container_names

    @pytest.mark.integration
    def test_remove(self) -> None:
        """Test removing a Docker container."""
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
        )

        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        assert container is not None

        DockerContainerManager.remove(self.TEST_CONTAINER_NAME)

        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        assert container is None

    @pytest.mark.integration
    def test_remove_nonexistent(self) -> None:
        """Test removing a nonexistent Docker container."""
        with pytest.raises(Exception):
            DockerContainerManager.remove(f"nonexistent-{uuid.uuid4()}")

    @pytest.mark.integration
    def test_start_container(self) -> None:
        """Test starting a Docker container."""
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            command="tail",
            args=["-f", "/dev/null"],  # Keep container running
        )

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status == "running"
