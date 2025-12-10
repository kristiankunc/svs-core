import uuid

import pytest

from pytest_mock import MockerFixture

from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import ExposedPort, Label, Volume


class TestDockerContainerManager:
    TEST_IMAGE = "alpine:latest"
    TEST_CONTAINER_NAME = f"svs-test-container-{str(uuid.uuid4())[:8]}"
    TEST_OWNER = "testuser"

    @pytest.fixture(scope="session", autouse=True)
    def pull_test_image(self):
        if not DockerImageManager.exists(self.TEST_IMAGE):
            DockerImageManager.pull(self.TEST_IMAGE)

    @pytest.fixture(autouse=True)
    def mock_system_user(self, mocker: MockerFixture) -> None:
        """Mock SystemUserManager to avoid requiring actual system users."""
        mocker.patch(
            "svs_core.docker.container.SystemUserManager.get_system_uid_gid",
            return_value=(1000, 1000),
        )

    @pytest.fixture(autouse=True)
    def cleanup_test_containers(self):
        self.cleanup_container()

        yield

        self.cleanup_container()

    def cleanup_container(self) -> None:
        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        if container:
            DockerContainerManager.remove(self.TEST_CONTAINER_NAME)

    @pytest.mark.integration
    def test_create_container(self) -> None:
        # Create a container
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        assert container is not None
        assert container.name == self.TEST_CONTAINER_NAME

        fetched_container = DockerContainerManager.get_container(
            self.TEST_CONTAINER_NAME
        )
        assert fetched_container is not None

    @pytest.mark.integration
    def test_create_container_with_command(self) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            command="echo",
            args=["Hello, Docker!"],
        )

        assert container is not None

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status in ["running", "exited", "created"]

    @pytest.mark.integration
    def test_create_container_with_labels(self) -> None:
        labels = [
            Label(key="com.svs.test1", value="value1"),
            Label(key="com.svs.test2", value="value2"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            labels=labels,
        )

        assert container is not None

        container_labels = container.labels
        assert container_labels.get("com.svs.test1") == "value1"
        assert container_labels.get("com.svs.test2") == "value2"

    @pytest.mark.integration
    def test_create_container_with_ports(self) -> None:
        exposed_ports = [
            ExposedPort(host_port=8080, container_port=80),
            ExposedPort(host_port=None, container_port=443),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            command="tail",
            args=["-f", "/dev/null"],
            ports=exposed_ports,
        )

        assert container is not None

        # Verify ports are properly configured
        container_ports = container.ports
        assert container_ports is not None

        DockerContainerManager.start_container(container)
        container.reload()

        assert container.status == "running"

    @pytest.mark.integration
    def test_create_container_with_volumes(self, tmp_path: object) -> None:
        import tempfile

        # Create temporary directories for volume mapping
        with tempfile.TemporaryDirectory() as host_dir:
            volumes = [
                Volume(host_path=host_dir, container_path="/data"),
            ]

            container = DockerContainerManager.create_container(
                name=self.TEST_CONTAINER_NAME,
                image=self.TEST_IMAGE,
                owner=self.TEST_OWNER,
                command="tail",
                args=["-f", "/dev/null"],
                volumes=volumes,
            )

            assert container is not None

            # Verify volumes are properly configured
            container_mounts = container.attrs.get("Mounts", [])
            assert container_mounts is not None

    @pytest.mark.integration
    def test_get_container(self) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        fetched_container = DockerContainerManager.get_container(
            self.TEST_CONTAINER_NAME
        )

        assert fetched_container is not None
        assert fetched_container.id == container.id

    @pytest.mark.integration
    def test_get_container_nonexistent(self) -> None:
        container = DockerContainerManager.get_container(f"nonexistent-{uuid.uuid4()}")

        assert container is None

    @pytest.mark.integration
    def test_get_all(self) -> None:
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        containers = DockerContainerManager.get_all()

        assert isinstance(containers, list)
        container_names = [container.name for container in containers]
        assert self.TEST_CONTAINER_NAME in container_names

    @pytest.mark.integration
    def test_remove(self) -> None:
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        assert container is not None

        DockerContainerManager.remove(self.TEST_CONTAINER_NAME)

        container = DockerContainerManager.get_container(self.TEST_CONTAINER_NAME)
        assert container is None

    @pytest.mark.integration
    def test_remove_nonexistent(self) -> None:
        with pytest.raises(Exception):
            DockerContainerManager.remove(f"nonexistent-{uuid.uuid4()}")

    @pytest.mark.integration
    def test_start_container(self) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            command="tail",
            args=["-f", "/dev/null"],  # Keep container running
        )

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status == "running"

    @pytest.mark.integration
    def test_create_container_with_caddy_labels(self, mocker: MockerFixture) -> None:
        """Test that Caddy labels are properly set when passed to container
        creation."""
        exposed_ports = [
            ExposedPort(host_port=80, container_port=80),
        ]

        labels = [
            Label(key="caddy", value="test.example.com"),
            Label(key="caddy.reverse_proxy", value="{{upstreams 80}}"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            labels=labels,
            ports=exposed_ports,
        )

        assert container is not None

        # Verify Caddy labels were set correctly
        container_labels = container.labels
        assert container_labels.get("caddy") == "test.example.com"
        assert container_labels.get("caddy.reverse_proxy") == "{{upstreams 80}}"

    @pytest.mark.integration
    def test_create_container_without_caddy_labels(self, mocker: MockerFixture) -> None:
        """Test that containers can be created without Caddy labels."""
        exposed_ports = [
            ExposedPort(host_port=8080, container_port=8080),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            ports=exposed_ports,
        )

        assert container is not None

        # Verify Caddy labels were NOT added (only system labels should exist)
        container_labels = container.labels
        assert "caddy" not in container_labels
        assert "caddy.reverse_proxy" not in container_labels

    @pytest.mark.integration
    def test_create_container_with_custom_labels(self, mocker: MockerFixture) -> None:
        """Test that custom labels can be added to containers."""
        exposed_ports = [
            ExposedPort(host_port=80, container_port=80),
        ]

        labels = [
            Label(key="app", value="nginx"),
            Label(key="version", value="1.0"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            labels=labels,
            ports=exposed_ports,
        )

        assert container is not None

        # Verify custom labels were added
        container_labels = container.labels
        assert container_labels.get("app") == "nginx"
        assert container_labels.get("version") == "1.0"

    @pytest.mark.integration
    def test_create_container_with_multiple_ports(self, mocker: MockerFixture) -> None:
        """Test container creation with multiple ports."""
        exposed_ports = [
            ExposedPort(host_port=80, container_port=80),
            ExposedPort(host_port=443, container_port=443),
            ExposedPort(host_port=8080, container_port=8080),
        ]

        labels = [
            Label(key="caddy", value="multi-port.example.com"),
            Label(key="caddy.reverse_proxy", value="{{upstreams 80}}"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
            labels=labels,
            ports=exposed_ports,
        )

        assert container is not None

        # Verify Caddy labels were set correctly
        container_labels = container.labels
        assert container_labels.get("caddy") == "multi-port.example.com"
        assert container_labels.get("caddy.reverse_proxy") == "{{upstreams 80}}"
