import uuid

from pathlib import Path

import pytest

from pytest_mock import MockerFixture

from svs_core.docker.base import get_docker_client
from svs_core.docker.container import DockerContainerManager
from svs_core.docker.image import DockerImageManager
from svs_core.docker.json_properties import ExposedPort, Label, Volume


class TestDockerContainerManager:
    TEST_IMAGE = "alpine:latest"
    TEST_CONTAINER_NAME = f"svs-test-container-{str(uuid.uuid4())[:8]}"
    TEST_OWNER = "testuser"
    LINUXSERVER_TEST_IMAGE = "lscr.io/linuxserver/test:latest"

    @pytest.fixture(scope="session", autouse=True)
    def pull_test_image(self):
        if not DockerImageManager.exists(self.TEST_IMAGE):
            DockerImageManager.pull(self.TEST_IMAGE)

        # Tag alpine as linuxserver image for testing
        # This allows us to test linuxserver-specific behavior without pulling
        # an actual linuxserver image
        if not DockerImageManager.exists(self.LINUXSERVER_TEST_IMAGE):
            try:
                client = get_docker_client()
                alpine_image = client.images.get(self.TEST_IMAGE)
                alpine_image.tag(self.LINUXSERVER_TEST_IMAGE)
            except Exception:
                pass  # If tagging fails, the test will be skipped

    @pytest.fixture(autouse=True)
    def mock_system_user(self, mocker: MockerFixture) -> None:
        """Mock SystemUserManager to avoid requiring actual system users."""
        mocker.patch(
            "svs_core.docker.container.SystemUserManager.get_system_uid_gid",
            return_value=(1000, 1000),
        )
        mocker.patch(
            "svs_core.docker.container.SystemUserManager.get_gid",
            return_value=1001,
        )

    @pytest.fixture(autouse=True)
    def mock_user(self, mocker: MockerFixture) -> None:
        """Mock User model."""
        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mocker.patch(
            "svs_core.docker.container.User.objects.get",
            return_value=mock_user,
        )

    @pytest.fixture()
    def mock_volumes_default(self, mocker: MockerFixture) -> None:
        """Mock SystemVolumeManager with default path.

        Use this fixture explicitly if needed.
        """
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
        )

    @pytest.fixture(autouse=True)
    def mock_volumes_default_autouse(self, mocker: MockerFixture) -> None:
        """Auto-mock SystemVolumeManager with default path."""
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
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
    def test_create_container_with_volumes(self, mocker: MockerFixture) -> None:
        import tempfile

        # Create temporary directories for volume mapping
        with tempfile.TemporaryDirectory() as host_dir:
            # Create a user-specific subdirectory within temp
            user_id = 1
            user_volume_dir = Path(host_dir) / str(user_id)
            user_volume_dir.mkdir(parents=True, exist_ok=True)
            data_dir = user_volume_dir / "data"
            data_dir.mkdir(parents=True, exist_ok=True)

            # Setup mocks that allow the temp directory structure
            mock_user = mocker.MagicMock()
            mock_user.id = user_id

            mocker.patch(
                "svs_core.docker.container.User.objects.get",
                return_value=mock_user,
            )
            mocker.patch(
                "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
                Path(host_dir),
            )

            volumes = [
                Volume(host_path=str(data_dir), container_path="/data"),
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

    @pytest.mark.integration
    def test_create_container_sets_user_for_regular_images(
        self, mocker: MockerFixture
    ) -> None:
        """Test that regular (non-linuxserver) images set user with UID:GID."""
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        assert container is not None
        # Verify user is set to UID:GID format
        assert container.attrs["Config"]["User"] == "1000:1001"

    @pytest.mark.integration
    def test_create_container_linuxserver_sets_puid_pgid(
        self, mocker: MockerFixture
    ) -> None:
        """Test that linuxserver images set PUID and PGID environment
        variables."""
        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.LINUXSERVER_TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        assert container is not None

        # Verify PUID and PGID are set in environment variables
        env_vars = container.attrs["Config"]["Env"]
        env_dict = {var.split("=")[0]: var.split("=", 1)[1] for var in env_vars}

        assert "PUID" in env_dict
        assert env_dict["PUID"] == "1000"
        assert "PGID" in env_dict
        assert env_dict["PGID"] == "1001"

    @pytest.mark.integration
    def test_create_container_uses_svs_admins_group(
        self, mocker: MockerFixture
    ) -> None:
        """Test that containers use svs-admins group for GID/PGID."""
        mock_get_gid = mocker.patch(
            "svs_core.docker.container.SystemUserManager.get_gid",
            return_value=1005,
        )

        container = DockerContainerManager.create_container(
            name=self.TEST_CONTAINER_NAME,
            image=self.TEST_IMAGE,
            owner=self.TEST_OWNER,
        )

        assert container is not None

        # Verify get_gid was called with svs-admins
        mock_get_gid.assert_called_with("svs-admins")

        # Verify GID is set correctly
        assert container.attrs["Config"]["User"] == "1000:1005"

    @pytest.mark.integration
    def test_create_container_with_volumes_permission_check(
        self, mocker: MockerFixture
    ) -> None:
        """Test that volumes are validated against user's base path."""
        # Mock the base path to /var/lib/svs/volumes with user ID 1
        base_path = Path("/var/lib/svs/volumes/1")
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
        )

        # Create a volume within the allowed path
        allowed_volume_path = str(base_path / "data")
        volumes = [
            Volume(host_path=allowed_volume_path, container_path="/data"),
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
        container_mounts = container.attrs.get("Mounts", [])
        assert container_mounts is not None

    @pytest.mark.integration
    def test_create_container_rejects_volume_outside_base_path(
        self, mocker: MockerFixture
    ) -> None:
        """Test that volumes outside user's base path are rejected."""
        # Mock the base path
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
        )

        # Try to create a volume outside the allowed path (user 2 instead of user 1)
        disallowed_volume_path = "/var/lib/svs/volumes/2/data"
        volumes = [
            Volume(host_path=disallowed_volume_path, container_path="/data"),
        ]

        with pytest.raises(PermissionError) as exc_info:
            DockerContainerManager.create_container(
                name=self.TEST_CONTAINER_NAME,
                image=self.TEST_IMAGE,
                owner=self.TEST_OWNER,
                volumes=volumes,
            )

        assert "outside the allowed directory" in str(exc_info.value)

    @pytest.mark.integration
    def test_create_container_rejects_volume_outside_user_directory(
        self, mocker: MockerFixture
    ) -> None:
        """Test that volumes outside the user's specific directory are
        rejected."""
        # Mock the base path
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
        )

        # Try to create a volume at a parent directory
        disallowed_volume_path = "/var/lib/svs/volumes"
        volumes = [
            Volume(host_path=disallowed_volume_path, container_path="/data"),
        ]

        with pytest.raises(PermissionError) as exc_info:
            DockerContainerManager.create_container(
                name=self.TEST_CONTAINER_NAME,
                image=self.TEST_IMAGE,
                owner=self.TEST_OWNER,
                volumes=volumes,
            )

        assert "outside the allowed directory" in str(exc_info.value)

    @pytest.mark.integration
    def test_create_container_with_multiple_volumes_all_allowed(
        self, mocker: MockerFixture
    ) -> None:
        """Test creating container with multiple volumes all within allowed
        path."""
        # Mock the base path
        mocker.patch(
            "svs_core.docker.container.SystemVolumeManager.BASE_PATH",
            Path("/var/lib/svs/volumes"),
        )

        base_path = Path("/var/lib/svs/volumes/1")
        volumes = [
            Volume(host_path=str(base_path / "data"), container_path="/data"),
            Volume(host_path=str(base_path / "logs"), container_path="/logs"),
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
        container_mounts = container.attrs.get("Mounts", [])
        assert len(container_mounts) == 2
