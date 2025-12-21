import pytest

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app


@pytest.mark.cli
class TestServiceCommands:
    runner: CliRunner

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_list_services_admin(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)
        mock_all = mocker.patch("svs_core.docker.service.Service.objects.all")
        mock_service = mocker.MagicMock()
        mock_service.id = 1
        mock_service.name = "test_service"
        mock_service.user.name = "admin"
        mock_service.user.id = 1
        mock_service.status = "running"
        mock_service.template.name = "test_template"
        mock_service.template.id = 1
        mock_all.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list"],
        )

        assert result.exit_code == 0
        # Table output should contain service name and status
        assert "test_service" in result.output
        assert "running" in result.output

    def test_list_services_non_admin(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.service.get_current_username", return_value="user1")
        mock_filter = mocker.patch("svs_core.docker.service.Service.objects.filter")
        mock_service = mocker.MagicMock()
        mock_service.id = 2
        mock_service.name = "user1_service"
        mock_service.user.name = "user1"
        mock_service.user.id = 2
        mock_service.status = "stopped"
        mock_service.template.name = "web_template"
        mock_service.template.id = 2
        mock_filter.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list"],
        )

        assert result.exit_code == 0
        # Table output should contain service name and status
        assert "user1_service" in result.output
        assert "stopped" in result.output

    def test_list_services_empty(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)
        mock_all = mocker.patch("svs_core.docker.service.Service.objects.all")
        mock_all.return_value = []

        result = self.runner.invoke(
            app,
            ["service", "list"],
        )

        assert result.exit_code == 0
        assert "No services found." in result.output

    def test_list_services_inline_admin(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)
        mock_all = mocker.patch("svs_core.docker.service.Service.objects.all")
        mock_service = mocker.MagicMock()
        mock_service.__str__.return_value = "Service(name='test_service')"
        mock_all.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list", "--inline"],
        )

        assert result.exit_code == 0
        assert "Service(name='test_service')" in result.output

    def test_list_services_inline_non_admin(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.service.get_current_username", return_value="user1")
        mock_filter = mocker.patch("svs_core.docker.service.Service.objects.filter")
        mock_service = mocker.MagicMock()
        mock_service.__str__.return_value = "Service(name='user1_service')"
        mock_filter.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list", "--inline"],
        )

        assert result.exit_code == 0
        assert "Service(name='user1_service')" in result.output

    def test_create_service(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "new_service"
        mock_service.id = 1
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            ["service", "create", "new_service", "1"],
        )

        assert result.exit_code == 0
        assert "Service 'new_service' created successfully with ID 1." in result.output

    def test_start_service_admin(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "other_user"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)

        result = self.runner.invoke(
            app,
            ["service", "start", "1"],
        )

        assert result.exit_code == 0
        assert "Service 'test_service' started successfully." in result.output
        mock_service.start.assert_called_once()

    def test_start_service_own(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "current_user"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "start", "1"],
        )

        assert result.exit_code == 0
        assert "Service 'test_service' started successfully." in result.output
        mock_service.start.assert_called_once()

    def test_start_service_unauthorized(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.user.name = "other_user"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "start", "1"],
        )

        assert result.exit_code == 1
        assert "You do not have permission to start this service." in result.output

    def test_create_service_with_domain(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "web_service"
        mock_service.id = 1
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            ["service", "create", "web_service", "1", "--domain", "example.com"],
        )

        assert result.exit_code == 0
        assert "Service 'web_service' created successfully with ID 1." in result.output
        mock_create.assert_called_once()
        # Verify domain was passed
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["domain"] == "example.com"

    def test_create_service_with_env_variables(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "db_service"
        mock_service.id = 2
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "db_service",
                "1",
                "--env",
                "DB_HOST=localhost",
                "--env",
                "DB_PORT=5432",
            ],
        )

        assert result.exit_code == 0
        assert "Service 'db_service' created successfully with ID 2." in result.output
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        env_vars = call_kwargs["override_env"]
        assert len(env_vars) == 2
        assert env_vars[0].key == "DB_HOST"
        assert env_vars[0].value == "localhost"
        assert env_vars[1].key == "DB_PORT"
        assert env_vars[1].value == "5432"

    def test_create_service_with_invalid_env_format(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.users.user.User.objects.get")

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "bad_service",
                "1",
                "--env",
                "INVALID_NO_EQUALS",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid environment variable format" in result.output
        assert "Use KEY=VALUE" in result.output

    def test_create_service_with_ports(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "web_service"
        mock_service.id = 3
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "web_service",
                "1",
                "--port",
                "80:8080",
                "--port",
                "443:8443",
            ],
        )

        assert result.exit_code == 0
        assert "Service 'web_service' created successfully with ID 3." in result.output
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        ports = call_kwargs["override_ports"]
        assert len(ports) == 2
        assert ports[0].container_port == 80
        assert ports[0].host_port == 8080
        assert ports[1].container_port == 443
        assert ports[1].host_port == 8443

    def test_create_service_with_invalid_port_format(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.users.user.User.objects.get")

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "bad_service",
                "1",
                "--port",
                "INVALID_NO_COLON",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid port format" in result.output
        assert "Use container_port:host_port" in result.output

    def test_create_service_with_invalid_port_numbers(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.users.user.User.objects.get")

        result = self.runner.invoke(
            app,
            ["service", "create", "bad_service", "1", "--port", "abc:def"],
        )

        assert result.exit_code == 1
        assert "Invalid port numbers" in result.output
        assert "Ports must be integers" in result.output

    def test_create_service_with_volumes(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "storage_service"
        mock_service.id = 4
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "storage_service",
                "1",
                "--volume",
                "/app/data:/data",
                "--volume",
                "/app/config:/etc/config",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Service 'storage_service' created successfully with ID 4." in result.output
        )
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        volumes = call_kwargs["override_volumes"]
        assert len(volumes) == 2
        assert volumes[0].container_path == "/app/data"
        assert volumes[0].host_path == "/data"
        assert volumes[1].container_path == "/app/config"
        assert volumes[1].host_path == "/etc/config"

    def test_create_service_with_invalid_volume_format(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.users.user.User.objects.get")

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "bad_service",
                "1",
                "--volume",
                "INVALID_NO_COLON",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid volume format" in result.output
        assert "Use container_path:host_path" in result.output

    def test_create_service_with_labels(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "labeled_service"
        mock_service.id = 5
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "labeled_service",
                "1",
                "--label",
                "environment=production",
                "--label",
                "version=1.0",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Service 'labeled_service' created successfully with ID 5." in result.output
        )
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        labels = call_kwargs["override_labels"]
        assert len(labels) == 2
        assert labels[0].key == "environment"
        assert labels[0].value == "production"
        assert labels[1].key == "version"
        assert labels[1].value == "1.0"

    def test_create_service_with_invalid_label_format(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.users.user.User.objects.get")

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "bad_service",
                "1",
                "--label",
                "INVALID_NO_EQUALS",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid label format" in result.output
        assert "Use KEY=VALUE" in result.output

    def test_create_service_with_command(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "cmd_service"
        mock_service.id = 6
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "cmd_service",
                "1",
                "--command",
                "/bin/bash -c 'echo hello'",
            ],
        )

        assert result.exit_code == 0
        assert "Service 'cmd_service' created successfully with ID 6." in result.output
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["override_command"] == "/bin/bash -c 'echo hello'"

    def test_create_service_with_args(self, mocker: MockerFixture) -> None:
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "args_service"
        mock_service.id = 7
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "args_service",
                "1",
                "--args",
                "arg1",
                "--args",
                "arg2",
                "--args",
                "arg3",
            ],
        )

        assert result.exit_code == 0
        assert "Service 'args_service' created successfully with ID 7." in result.output
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        args = call_kwargs["override_args"]
        assert len(args) == 3
        assert args[0] == "arg1"
        assert args[1] == "arg2"
        assert args[2] == "arg3"

    def test_create_service_with_all_overrides(self, mocker: MockerFixture) -> None:
        """Test creating a service with all override parameters."""
        mock_user = mocker.MagicMock()
        mock_user_get = mocker.patch("svs_core.users.user.User.objects.get")
        mock_user_get.return_value = mock_user

        mock_create = mocker.patch(
            "svs_core.docker.service.Service.create_from_template"
        )
        mock_service = mocker.MagicMock()
        mock_service.name = "full_service"
        mock_service.id = 8
        mock_create.return_value = mock_service

        result = self.runner.invoke(
            app,
            [
                "service",
                "create",
                "full_service",
                "1",
                "--domain",
                "full.example.com",
                "--env",
                "VAR1=value1",
                "--env",
                "VAR2=value2",
                "--port",
                "80:8080",
                "--volume",
                "/app:/data",
                "--label",
                "env=prod",
                "--command",
                "/start.sh",
                "--args",
                "worker",
                "--args",
                "4",
            ],
        )

        assert result.exit_code == 0
        assert "Service 'full_service' created successfully with ID 8." in result.output
        mock_create.assert_called_once()
        call_kwargs = mock_create.call_args[1]
        assert call_kwargs["domain"] == "full.example.com"
        assert len(call_kwargs["override_env"]) == 2
        assert len(call_kwargs["override_ports"]) == 1
        assert len(call_kwargs["override_volumes"]) == 1
        assert len(call_kwargs["override_labels"]) == 1
        assert call_kwargs["override_command"] == "/start.sh"
        assert len(call_kwargs["override_args"]) == 2

    def test_stop_service_admin(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "other_user"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)

        result = self.runner.invoke(
            app,
            ["service", "stop", "1"],
        )

        assert result.exit_code == 0
        assert "Service 'test_service' stopped successfully." in result.output
        mock_service.stop.assert_called_once()

    def test_logs_admin(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "other_user"
        mock_service.get_logs.return_value = "Log line 1\nLog line 2\nLog line 3"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)

        result = self.runner.invoke(
            app,
            ["service", "logs", "1"],
        )

        assert result.exit_code == 0
        assert "Log line 1" in result.output
        assert "Log line 2" in result.output
        assert "Log line 3" in result.output
        mock_service.get_logs.assert_called_once()

    def test_logs_own_service(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "current_user"
        mock_service.get_logs.return_value = "Container logs here"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "logs", "1"],
        )

        assert result.exit_code == 0
        assert "Container logs here" in result.output
        mock_service.get_logs.assert_called_once()

    def test_logs_unauthorized(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.user.name = "other_user"
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "logs", "1"],
        )

        assert result.exit_code == 1
        assert (
            "You do not have permission to view this service's logs." in result.output
        )

    def test_logs_empty(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.service.Service.objects.get")
        mock_service = mocker.MagicMock()
        mock_service.name = "test_service"
        mock_service.user.name = "current_user"
        mock_service.get_logs.return_value = ""
        mock_get.return_value = mock_service
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "logs", "1"],
        )

        assert result.exit_code == 0
        mock_service.get_logs.assert_called_once()

    def test_build_service_success(self, mocker: MockerFixture) -> None:
        """Test building a service via CLI."""
        mock_service = mocker.MagicMock()
        mock_service.id = 1
        mock_service.name = "test_build_service"
        mock_service.user.name = "current_user"

        mocker.patch(
            "svs_core.cli.service.get_or_exit", return_value=mock_service
        )
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "build", "1", "/tmp/source"],
        )

        assert result.exit_code == 0
        assert "built successfully" in result.output
        mock_service.build.assert_called_once()

    def test_build_service_permission_denied(self, mocker: MockerFixture) -> None:
        """Test building a service without permission."""
        mock_service = mocker.MagicMock()
        mock_service.id = 1
        mock_service.name = "test_service"
        mock_service.user.name = "other_user"

        mocker.patch(
            "svs_core.cli.service.get_or_exit", return_value=mock_service
        )
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch(
            "svs_core.cli.service.get_current_username", return_value="current_user"
        )

        result = self.runner.invoke(
            app,
            ["service", "build", "1", "/tmp/source"],
        )

        assert result.exit_code == 1
        assert "permission" in result.output.lower()
        mock_service.build.assert_not_called()

    def test_build_service_admin_can_build_any(self, mocker: MockerFixture) -> None:
        """Test that admin can build any service."""
        mock_service = mocker.MagicMock()
        mock_service.id = 1
        mock_service.name = "other_user_service"
        mock_service.user.name = "other_user"

        mocker.patch(
            "svs_core.cli.service.get_or_exit", return_value=mock_service
        )
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=True)

        result = self.runner.invoke(
            app,
            ["service", "build", "1", "/tmp/source"],
        )

        assert result.exit_code == 0
        assert "built successfully" in result.output
        mock_service.build.assert_called_once()
