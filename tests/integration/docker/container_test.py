import uuid

import pytest

from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import ExposedPort, Label, Volume
from svs_core.users.user import User


class TestDockerContainerManager:
    TEST_IMAGE = "alpine:latest"
    TEST_CONTAINER_NAME = f"svs-test-container-{str(uuid.uuid4())[:8]}"

    @pytest.fixture(scope="session", autouse=True)
    def pull_test_image(self):
        if not DockerImageManager.exists(self.TEST_IMAGE):
            DockerImageManager.pull(self.TEST_IMAGE)

    @pytest.fixture
    def test_user(self, mocker, db):
        """Create a mock test user with uid/gid set to 1000."""
        mocker.patch("svs_core.users.user.DockerNetworkManager.create_network")
        mocker.patch("svs_core.users.user.SystemUserManager.create_user")
        mocker.patch("svs_core.users.user.SystemUserManager.get_uid", return_value=1000)
        mocker.patch("svs_core.users.user.SystemUserManager.get_gid", return_value=1000)

        user = User.create(
            name=f"testuser-{str(uuid.uuid4())[:8]}", password="password123"
        )
        return user

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
    def test_create_container(self, test_user: User) -> None:
        # Create a container
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
        )

        assert container is not None
        assert container.name == self.TEST_CONTAINER_NAME

        fetched_container = DockerContainerManager.get_container(
            self.TEST_CONTAINER_NAME
        )
        assert fetched_container is not None

    @pytest.mark.integration
    def test_create_container_with_command(self, test_user: User) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
            command="echo",
            args=["Hello, Docker!"],
        )

        assert container is not None

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status in ["running", "exited", "created"]

    @pytest.mark.integration
    def test_create_container_with_labels(self, test_user: User) -> None:
        labels = [
            Label(key="com.svs.test1", value="value1"),
            Label(key="com.svs.test2", value="value2"),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
            labels=labels,
        )

        assert container is not None

        container_labels = container.labels
        assert container_labels.get("com.svs.test1") == "value1"
        assert container_labels.get("com.svs.test2") == "value2"

    @pytest.mark.integration
    def test_create_container_with_ports(self, test_user: User) -> None:
        exposed_ports = [
            ExposedPort(host_port=8080, container_port=80),
            ExposedPort(host_port=None, container_port=443),
        ]

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
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
    def test_create_container_with_volumes(self, test_user: User) -> None:
        import tempfile

        # Create temporary directories for volume mapping
        with tempfile.TemporaryDirectory() as host_dir:
            volumes = [
                Volume(host_path=host_dir, container_path="/data"),
            ]

            container = DockerContainerManager.create_container(
                name=self.TEST_CONTAINER_NAME,
                image=self.TEST_IMAGE,
                user=test_user,
                command="tail",
                args=["-f", "/dev/null"],
                volumes=volumes,
            )

            assert container is not None

            # Verify volumes are properly configured
            container_mounts = container.attrs.get("Mounts", [])
            assert container_mounts is not None

    @pytest.mark.integration
    def test_get_container(self, test_user: User) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
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
    def test_get_all(self, test_user: User) -> None:
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
        )

        containers = DockerContainerManager.get_all()

        assert isinstance(containers, list)
        container_names = [container.name for container in containers]
        assert self.TEST_CONTAINER_NAME in container_names

    @pytest.mark.integration
    def test_remove(self, test_user: User) -> None:
        DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
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
    def test_start_container(self, test_user: User) -> None:
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
            command="tail",
            args=["-f", "/dev/null"],  # Keep container running
        )

        DockerContainerManager.start_container(container)

        container.reload()
        assert container.status == "running"

    @pytest.mark.integration
    @pytest.mark.django_db
    def test_create_container_with_uid_gid(self, test_user: User) -> None:
        # Create a container with the user
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            user=test_user,
            command="tail",
            args=["-f", "/dev/null"],
        )

        assert container is not None

        # Verify that the container is configured with the correct uid:gid
        # Check the container configuration
        assert container.attrs is not None
        config = container.attrs.get("Config", {})
        user_field = config.get("User", "")
        assert user_field == "1000:1000"
