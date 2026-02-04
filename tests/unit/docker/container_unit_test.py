import pytest

from pytest_mock import MockerFixture

from svs_core.docker.container import DockerContainerManager
from svs_core.docker.json_properties import EnvVariable, ExposedPort, Volume
from svs_core.shared.exceptions import ServiceOperationException


class TestDockerContainerManagerUnit:
    @pytest.mark.unit
    def test_has_config_changed_image_different(self, mocker: MockerFixture) -> None:
        """Test has_config_changed detects image change."""
        # Mock container with different image
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:old",
                "Cmd": ["nginx", "-g", "daemon off;"],
                "Env": [],
            },
            "NetworkSettings": {"Ports": {}},
            "Mounts": [],
        }

        # Mock service with different image
        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx -g daemon off;"
        mock_service.environment_variables = []
        mock_service.ports = []
        mock_service.volumes = []

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is True
        mock_container.reload.assert_called_once()

    @pytest.mark.unit
    def test_has_config_changed_command_different(self, mocker: MockerFixture) -> None:
        """Test has_config_changed detects command change."""
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:latest",
                "Cmd": ["nginx", "-g", "daemon off;"],
                "Env": [],
            },
            "NetworkSettings": {"Ports": {}},
            "Mounts": [],
        }

        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx -g daemon on;"  # Different command
        mock_service.environment_variables = []
        mock_service.ports = []
        mock_service.volumes = []

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is True

    @pytest.mark.unit
    def test_has_config_changed_env_different(self, mocker: MockerFixture) -> None:
        """Test has_config_changed detects environment variable changes."""
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:latest",
                "Cmd": ["nginx"],
                "Env": ["VAR1=value1"],
            },
            "NetworkSettings": {"Ports": {}},
            "Mounts": [],
        }

        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.environment_variables = [
            EnvVariable(key="VAR1", value="value1"),
            EnvVariable(key="VAR2", value="value2"),  # Additional env var
        ]
        mock_service.ports = []
        mock_service.volumes = []

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is True

    @pytest.mark.unit
    def test_has_config_changed_ports_different(self, mocker: MockerFixture) -> None:
        """Test has_config_changed detects port changes."""
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:latest",
                "Cmd": ["nginx"],
                "Env": [],
            },
            "NetworkSettings": {"Ports": {"80/tcp": None}},
            "Mounts": [],
        }

        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.environment_variables = []
        mock_service.ports = [
            ExposedPort(host_port=8080, container_port=80),
            ExposedPort(host_port=8443, container_port=443),  # Additional port
        ]
        mock_service.volumes = []

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is True

    @pytest.mark.unit
    def test_has_config_changed_volumes_different(self, mocker: MockerFixture) -> None:
        """Test has_config_changed detects volume changes."""
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:latest",
                "Cmd": ["nginx"],
                "Env": [],
            },
            "NetworkSettings": {"Ports": {}},
            "Mounts": [{"Destination": "/data"}],
        }

        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.environment_variables = []
        mock_service.ports = []
        mock_service.volumes = [
            Volume(host_path="/tmp/data", container_path="/data"),
            Volume(host_path="/tmp/config", container_path="/config"),  # Additional
        ]

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is True

    @pytest.mark.unit
    def test_has_config_changed_no_change(self, mocker: MockerFixture) -> None:
        """Test has_config_changed returns False when config is the same."""
        mock_container = mocker.MagicMock()
        mock_container.reload = mocker.MagicMock()
        mock_container.attrs = {
            "Config": {
                "Image": "nginx:latest",
                "Cmd": ["nginx"],
                "Env": ["VAR1=value1"],
            },
            "NetworkSettings": {"Ports": {"80/tcp": None}},
            "Mounts": [{"Destination": "/data"}],
        }

        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.environment_variables = [EnvVariable(key="VAR1", value="value1")]
        mock_service.ports = [ExposedPort(host_port=8080, container_port=80)]
        mock_service.volumes = [Volume(host_path="/tmp/data", container_path="/data")]

        result = DockerContainerManager.has_config_changed(
            mock_container, mock_service
        )

        assert result is False

    @pytest.mark.unit
    def test_recreate_container_stops_running_container(
        self, mocker: MockerFixture
    ) -> None:
        """Test recreate_container stops a running container before recreating."""
        # Mock running container
        mock_container = mocker.MagicMock()
        mock_container.name = "test-container"
        mock_container.id = "old-container-id"
        mock_container.status = "running"
        mock_container.stop = mocker.MagicMock()
        mock_container.remove = mocker.MagicMock()

        # Mock service
        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.args = []
        mock_service.labels = []
        mock_service.exposed_ports = []
        mock_service.volumes = []
        mock_service.env = []
        mock_service.user.name = "testuser"

        # Mock new container creation
        mock_new_container = mocker.MagicMock()
        mock_new_container.id = "new-container-id"
        mock_create = mocker.patch(
            "svs_core.docker.container.DockerContainerManager.create_container",
            return_value=mock_new_container,
        )

        result = DockerContainerManager.recreate_container(
            mock_container, mock_service
        )

        # Verify container was stopped and removed
        mock_container.stop.assert_called_once()
        mock_container.remove.assert_called_once_with(force=True)

        # Verify new container was created with correct parameters
        mock_create.assert_called_once_with(
            name="test-container",
            image="nginx:latest",
            owner="testuser",
            command="nginx",
            args=[],
            labels=[],
            ports=[],
            volumes=[],
            environment_variables=[],
        )

        # Verify new container is returned
        assert result == mock_new_container

    @pytest.mark.unit
    def test_recreate_container_handles_stopped_container(
        self, mocker: MockerFixture
    ) -> None:
        """Test recreate_container handles already stopped containers."""
        # Mock stopped container
        mock_container = mocker.MagicMock()
        mock_container.name = "test-container"
        mock_container.id = "old-container-id"
        mock_container.status = "exited"
        mock_container.stop = mocker.MagicMock()
        mock_container.remove = mocker.MagicMock()

        # Mock service
        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.command = "nginx"
        mock_service.args = []
        mock_service.labels = []
        mock_service.exposed_ports = []
        mock_service.volumes = []
        mock_service.env = []
        mock_service.user.name = "testuser"

        # Mock new container creation
        mock_new_container = mocker.MagicMock()
        mock_create = mocker.patch(
            "svs_core.docker.container.DockerContainerManager.create_container",
            return_value=mock_new_container,
        )

        result = DockerContainerManager.recreate_container(
            mock_container, mock_service
        )

        # Verify container was not stopped (already stopped)
        mock_container.stop.assert_not_called()

        # Verify container was removed
        mock_container.remove.assert_called_once_with(force=True)

        # Verify new container was created
        mock_create.assert_called_once()
        assert result == mock_new_container

    @pytest.mark.unit
    def test_recreate_container_raises_on_stop_failure(
        self, mocker: MockerFixture
    ) -> None:
        """Test recreate_container raises ServiceOperationException on stop failure."""
        # Mock container that fails to stop
        mock_container = mocker.MagicMock()
        mock_container.name = "test-container"
        mock_container.id = "container-id"
        mock_container.status = "running"
        mock_container.stop.side_effect = Exception("Failed to stop")

        mock_service = mocker.MagicMock()

        with pytest.raises(ServiceOperationException, match="Failed to stop container"):
            DockerContainerManager.recreate_container(mock_container, mock_service)

    @pytest.mark.unit
    def test_recreate_container_raises_on_remove_failure(
        self, mocker: MockerFixture
    ) -> None:
        """Test recreate_container raises ServiceOperationException on remove failure."""
        # Mock container that fails to remove
        mock_container = mocker.MagicMock()
        mock_container.name = "test-container"
        mock_container.id = "container-id"
        mock_container.status = "exited"
        mock_container.remove.side_effect = Exception("Failed to remove")

        mock_service = mocker.MagicMock()

        with pytest.raises(
            ServiceOperationException, match="Failed to remove container"
        ):
            DockerContainerManager.recreate_container(mock_container, mock_service)

    @pytest.mark.unit
    def test_recreate_container_raises_on_create_failure(
        self, mocker: MockerFixture
    ) -> None:
        """Test recreate_container raises ServiceOperationException on create failure."""
        # Mock container
        mock_container = mocker.MagicMock()
        mock_container.name = "test-container"
        mock_container.id = "container-id"
        mock_container.status = "exited"
        mock_container.remove = mocker.MagicMock()

        # Mock service
        mock_service = mocker.MagicMock()
        mock_service.image = "nginx:latest"
        mock_service.user.name = "testuser"

        # Mock create_container to fail
        mocker.patch(
            "svs_core.docker.container.DockerContainerManager.create_container",
            side_effect=Exception("Failed to create"),
        )

        with pytest.raises(
            ServiceOperationException, match="Failed to recreate container"
        ):
            DockerContainerManager.recreate_container(mock_container, mock_service)
