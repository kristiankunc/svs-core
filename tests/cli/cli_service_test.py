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
        mock_service.__str__.return_value = "Service(name='test_service')"
        mock_all.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list"],
        )

        assert result.exit_code == 0
        assert "- Service(name='test_service')" in result.output

    def test_list_services_non_admin(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.service.is_current_user_admin", return_value=False)
        mocker.patch("svs_core.cli.service.get_current_username", return_value="user1")
        mock_filter = mocker.patch("svs_core.docker.service.Service.objects.filter")
        mock_service = mocker.MagicMock()
        mock_service.__str__.return_value = "Service(name='user1_service')"
        mock_filter.return_value = [mock_service]

        result = self.runner.invoke(
            app,
            ["service", "list"],
        )

        assert result.exit_code == 0
        assert "- Service(name='user1_service')" in result.output

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
            ["service", "create", "new_service", "1", "1"],
        )

        assert result.exit_code == 0
        assert (
            "✅ Service 'new_service' created successfully with ID 1." in result.output
        )

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
        assert "✅ Service 'test_service' started successfully." in result.output
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
        assert "✅ Service 'test_service' started successfully." in result.output
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

        assert result.exit_code == 0
        assert "❌ You do not have permission to start this service." in result.output

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
        assert "✅ Service 'test_service' stopped successfully." in result.output
        mock_service.stop.assert_called_once()
