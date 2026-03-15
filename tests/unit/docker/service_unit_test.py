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
        """Test that Service.recreate raises exception when container_id is
        None."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = None

        # Call the actual recreate method
        with pytest.raises(
            ServiceOperationException, match="Service does not have a container ID"
        ):
            Service.recreate(mock_service)

    @pytest.mark.unit
    def test_recreate_container_not_found(self, mocker: MockerFixture) -> None:
        """Test that Service.recreate raises exception when container is not
        found."""
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
        mock_service.status = ServiceStatus.EXITED
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
        """Test that Service.recreate restarts a running service after
        recreation."""
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
        """Test that Service.recreate connects to caddy network when label is
        present."""
        # Create mock service with caddy label
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "old-container-id"
        mock_service.name = "test-service"
        mock_service.status = ServiceStatus.EXITED
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

    # --- update() tests ---

    @pytest.mark.unit
    def test_update_sets_domain(self, mocker: MockerFixture) -> None:
        """Test that update sets domain and calls save/recreate."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.domain = "old.example.com"
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        Service.update(mock_service, domain="new.example.com")

        assert mock_service.domain == "new.example.com"
        mock_service.save.assert_called_once()
        mock_service.recreate.assert_called_once()

    @pytest.mark.unit
    def test_update_sets_env_variables(self, mocker: MockerFixture) -> None:
        """Test that update replaces env variables."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.env = []
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        new_env = [EnvVariable(key="KEY", value="VALUE")]
        Service.update(mock_service, env_variables=new_env)

        assert mock_service.env == new_env
        mock_service.save.assert_called_once()

    @pytest.mark.unit
    def test_update_sets_ports(self, mocker: MockerFixture) -> None:
        """Test that update replaces exposed ports."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.exposed_ports = []
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        new_ports = [ExposedPort(container_port=80, host_port=8080)]
        Service.update(mock_service, ports=new_ports)

        assert mock_service.exposed_ports == new_ports
        mock_service.save.assert_called_once()

    @pytest.mark.unit
    def test_update_sets_command(self, mocker: MockerFixture) -> None:
        """Test that update sets command."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.command = None
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        Service.update(mock_service, command="python app.py")

        assert mock_service.command == "python app.py"

    @pytest.mark.unit
    def test_update_sets_args(self, mocker: MockerFixture) -> None:
        """Test that update sets args."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.args = []
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        Service.update(mock_service, args=["--debug", "--reload"])

        assert mock_service.args == ["--debug", "--reload"]

    @pytest.mark.unit
    def test_update_noop_calls_save_and_recreate(self, mocker: MockerFixture) -> None:
        """Test that update with no arguments still calls save and recreate."""
        mock_service = mocker.MagicMock(spec=Service)
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        Service.update(mock_service)

        mock_service.save.assert_called_once()
        mock_service.recreate.assert_called_once()

    @pytest.mark.unit
    def test_update_invalid_domain_type(self, mocker: MockerFixture) -> None:
        """Test that update raises ValidationException for non-string
        domain."""
        mock_service = mocker.MagicMock(spec=Service)

        with pytest.raises(ValidationException, match="Domain must be a string"):
            Service.update(mock_service, domain=123)  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_update_invalid_port_container_port(self, mocker: MockerFixture) -> None:
        """Test that update raises ValidationException for non-positive
        container port."""
        mock_service = mocker.MagicMock(spec=Service)

        with pytest.raises(
            ValidationException, match="Container port must be a positive integer"
        ):
            Service.update(
                mock_service,
                ports=[ExposedPort(container_port=-1, host_port=8080)],
            )

    @pytest.mark.unit
    def test_update_invalid_command_type(self, mocker: MockerFixture) -> None:
        """Test that update raises ValidationException for non-string
        command."""
        mock_service = mocker.MagicMock(spec=Service)

        with pytest.raises(ValidationException, match="Command must be a string"):
            Service.update(mock_service, command=123)  # type: ignore[arg-type]

    @pytest.mark.unit
    def test_update_invalid_arg_item(self, mocker: MockerFixture) -> None:
        """Test that update raises ValidationException for non-string arg
        items."""
        mock_service = mocker.MagicMock(spec=Service)

        with pytest.raises(ValidationException, match="Each argument must be a string"):
            Service.update(mock_service, args=[123])  # type: ignore[list-item]

    @pytest.mark.unit
    def test_update_none_values_preserve_existing(self, mocker: MockerFixture) -> None:
        """Test that None values leave existing fields unchanged."""
        original_env = [EnvVariable(key="ORIGINAL", value="yes")]
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.domain = "original.com"
        mock_service.env = original_env
        mocker.patch.object(Service, "save")
        mocker.patch.object(Service, "recreate")

        Service.update(mock_service, domain=None, env_variables=None)

        assert mock_service.domain == "original.com"
        assert mock_service.env is original_env

    # --- healthcheck_status property tests ---

    @pytest.mark.unit
    def test_healthcheck_status_returns_none_when_container_not_found(
        self, mocker: MockerFixture
    ) -> None:
        """Test that healthcheck_status returns None when container is not
        found."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "missing-container-id"

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=None,
        )

        result = Service.healthcheck_status.fget(  # type: ignore[attr-defined]
            mock_service
        )

        assert result is None

    @pytest.mark.unit
    def test_healthcheck_status_returns_healthy(self, mocker: MockerFixture) -> None:
        """Test that healthcheck_status returns 'healthy' for a healthy
        container."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "container-id"

        mock_container = mocker.MagicMock()
        mock_container.attrs = {"State": {"Health": {"Status": "healthy"}}}

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )

        result = Service.healthcheck_status.fget(  # type: ignore[attr-defined]
            mock_service
        )

        assert result == "healthy"

    @pytest.mark.unit
    def test_healthcheck_status_returns_unhealthy(self, mocker: MockerFixture) -> None:
        """Test that healthcheck_status returns 'unhealthy' for an unhealthy
        container."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "container-id"

        mock_container = mocker.MagicMock()
        mock_container.attrs = {"State": {"Health": {"Status": "unhealthy"}}}

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )

        result = Service.healthcheck_status.fget(  # type: ignore[attr-defined]
            mock_service
        )

        assert result == "unhealthy"

    @pytest.mark.unit
    def test_healthcheck_status_returns_starting(self, mocker: MockerFixture) -> None:
        """Test that healthcheck_status returns 'starting' for a starting
        container."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "container-id"

        mock_container = mocker.MagicMock()
        mock_container.attrs = {"State": {"Health": {"Status": "starting"}}}

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )

        result = Service.healthcheck_status.fget(  # type: ignore[attr-defined]
            mock_service
        )

        assert result == "starting"

    @pytest.mark.unit
    def test_healthcheck_status_returns_none_for_unknown_status(
        self, mocker: MockerFixture
    ) -> None:
        """Test that healthcheck_status returns None for an unknown/missing
        health status."""
        mock_service = mocker.MagicMock(spec=Service)
        mock_service.container_id = "container-id"

        mock_container = mocker.MagicMock()
        # No Health key — falls back to "None"
        mock_container.attrs = {"State": {}}

        mocker.patch(
            "svs_core.docker.service.DockerContainerManager.get_container",
            return_value=mock_container,
        )

        res = Service.healthcheck_status.fget(  # type: ignore[attr-defined]
            mock_service
        )

        assert res is None
