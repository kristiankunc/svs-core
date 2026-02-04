import pytest

from pytest_mock import MockerFixture

from svs_core.db.models import ServiceStatus
from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Label,
    Volume,
)
from svs_core.docker.service import Service
from svs_core.shared.exceptions import ServiceOperationException, ValidationException


class TestServiceUnit:
    @pytest.mark.unit
    def test_merge_overrides_with_labels(self):
        base = [Label(key="A", value="1"), Label(key="B", value="2")]
        overrides = [Label(key="B", value="3"), Label(key="C", value="4")]

        result = Service._merge_overrides(base, overrides)

        assert len(result) == 3

        result_dict = {item.key: item.value for item in result}
        assert result_dict["A"] == "1"
        assert result_dict["B"] == "3"
        assert result_dict["C"] == "4"

    @pytest.mark.unit
    def test_merge_overrides_with_env_variables(self):
        base = [
            EnvVariable(key="A", value="1"),
            EnvVariable(key="B", value="2"),
        ]
        overrides = [
            EnvVariable(key="B", value="3"),
            EnvVariable(key="C", value="4"),
        ]

        result = Service._merge_overrides(base, overrides)

        assert len(result) == 3

        result_dict = {item.key: item.value for item in result}
        assert result_dict["A"] == "1"
        assert result_dict["B"] == "3"
        assert result_dict["C"] == "4"

    @pytest.mark.unit
    def test_merge_overrides_with_volumes(self):
        base = [
            Volume(host_path="A", container_path="1"),
            Volume(host_path="B", container_path="2"),
        ]
        overrides = [
            Volume(host_path="B", container_path="3"),
            Volume(host_path="override", container_path="1"),
        ]

        result = Service._merge_overrides(base, overrides)

        assert len(result) == 3

        result_dict = {item.container_path: item.host_path for item in result}
        assert result_dict["1"] == "override"
        assert result_dict["2"] == "B"
        assert result_dict["3"] == "B"

    @pytest.mark.unit
    def test_create_validates_domain_type(self, mocker: MockerFixture) -> None:
        """Test that Service.create validates domain parameter type."""
        mock_template = mocker.MagicMock()
        mock_template.id = 1
        mocker.patch(
            "svs_core.docker.service.Template.objects.get", return_value=mock_template
        )

        mock_user = mocker.MagicMock()
        mock_user.id = 1

        # Test with non-string domain
        with pytest.raises(ValidationException, match="Domain must be a string"):
            Service.create(
                name="test-service",
                template_id=1,
                user=mock_user,
                domain=123,  # type: ignore[arg-type]
            )

    @pytest.mark.unit
    def test_create_accepts_valid_domain(self, mocker: MockerFixture) -> None:
        """Test that Service.create accepts valid domain string."""
        mock_template = mocker.MagicMock()
        mock_template.id = 1
        mock_template.image = "nginx:latest"
        mock_template.default_env = []
        mock_template.default_ports = []
        mock_template.default_volumes = []
        mock_template.labels = []
        mock_template.healthcheck = None
        mock_template.start_cmd = None
        mock_template.args = []
        mock_template.default_contents = []

        mocker.patch(
            "svs_core.docker.service.Template.objects.get", return_value=mock_template
        )
        mocker.patch("svs_core.docker.service.Service.objects.create")

        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mock_user.name = "testuser"

        # Should not raise any exception
        Service.create(
            name="test-service",
            template_id=1,
            user=mock_user,
            domain="example.com",
        )

    @pytest.mark.unit
    def test_create_accepts_none_domain(self, mocker: MockerFixture) -> None:
        """Test that Service.create accepts None as domain value."""
        mock_template = mocker.MagicMock()
        mock_template.id = 1
        mock_template.image = "nginx:latest"
        mock_template.default_env = []
        mock_template.default_ports = []
        mock_template.default_volumes = []
        mock_template.labels = []
        mock_template.healthcheck = None
        mock_template.start_cmd = None
        mock_template.args = []
        mock_template.default_contents = []

        mocker.patch(
            "svs_core.docker.service.Template.objects.get", return_value=mock_template
        )
        mocker.patch("svs_core.docker.service.Service.objects.create")

        mock_user = mocker.MagicMock()
        mock_user.id = 1
        mock_user.name = "testuser"

        # Should not raise any exception
        Service.create(
            name="test-service",
            template_id=1,
            user=mock_user,
            domain=None,
        )

    @pytest.mark.unit
    def test_recreate_without_container_id(self, mocker: MockerFixture) -> None:
        """Test that Service.recreate raises exception when container_id is None."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = None

        # Call the actual recreate method
        with pytest.raises(
            ServiceOperationException, match="Service does not have a container ID"
        ):
            Service.recreate(mock_service)

    @pytest.mark.unit
    def test_recreate_container_not_found(self, mocker: MockerFixture) -> None:
        """Test that Service.recreate raises exception when container is not found."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "missing-container-id"

        # Mock get_container to return None
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=None,
        )

        # Call the actual recreate method
        with pytest.raises(
            ServiceOperationException, match="Container with ID .* not found"
        ):
            Service.recreate(mock_service)

    @pytest.mark.unit
    def test_recreate_success(self, mocker: MockerFixture) -> None:
        """Test successful service recreation."""
        # Create mock service
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "old-container-id"
        mock_service.name = "test-service"
        mock_service.status = ServiceStatus.STOPPED
        mock_service.user.name = "testuser"
        mock_service.labels = [Label(key="test", value="label")]

        # Mock old container
        mock_old_container = mocker.MagicMock()
        mock_old_container.id = "old-container-id"

        # Mock new container
        mock_new_container = mocker.MagicMock()
        mock_new_container.id = "new-container-id"
        mock_new_container.start = mocker.MagicMock()

        # Mock dependencies
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_old_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.recreate_container",
            return_value=mock_new_container,
        )
        mock_connect = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Call the actual recreate method
        Service.recreate(mock_service)

        # Verify the service was updated with new container ID
        assert mock_service.container_id == "new-container-id"

        # Verify save was called
        mock_service.save.assert_called()

        # Verify networks were connected
        mock_connect.assert_any_call(mock_new_container, "testuser")

        # Verify container was not started (status was STOPPED)
        mock_new_container.start.assert_not_called()

    @pytest.mark.unit
    def test_recreate_restarts_running_service(self, mocker: MockerFixture) -> None:
        """Test that Service.recreate restarts a running service after recreation."""
        # Create mock service with RUNNING status
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "old-container-id"
        mock_service.name = "test-service"
        mock_service.status = ServiceStatus.RUNNING
        mock_service.user.name = "testuser"
        mock_service.labels = []

        # Mock containers
        mock_old_container = mocker.MagicMock()
        mock_new_container = mocker.MagicMock()
        mock_new_container.id = "new-container-id"
        mock_new_container.start = mocker.MagicMock()

        # Mock dependencies
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_old_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.recreate_container",
            return_value=mock_new_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Call the actual recreate method
        Service.recreate(mock_service)

        # Verify container was started (status was RUNNING)
        mock_new_container.start.assert_called_once()

    @pytest.mark.unit
    def test_recreate_connects_to_caddy_network(self, mocker: MockerFixture) -> None:
        """Test that Service.recreate connects to caddy network when label is present."""
        # Create mock service with caddy label
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "old-container-id"
        mock_service.name = "test-service"
        mock_service.status = ServiceStatus.STOPPED
        mock_service.user.name = "testuser"
        mock_service.labels = [Label(key="caddy", value="example.com")]

        # Mock containers
        mock_old_container = mocker.MagicMock()
        mock_new_container = mocker.MagicMock()
        mock_new_container.id = "new-container-id"

        # Mock dependencies
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_old_container,
        )
        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.recreate_container",
            return_value=mock_new_container,
        )
        mock_connect = mocker.patch(
            "svs_core.docker.service.DockerContainerManager.connect_to_network"
        )

        # Call the actual recreate method
        Service.recreate(mock_service)

        # Verify both user and caddy networks were connected
        assert mock_connect.call_count == 2
        mock_connect.assert_any_call(mock_new_container, "testuser")
        mock_connect.assert_any_call(mock_new_container, "caddy")
