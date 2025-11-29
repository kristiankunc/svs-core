import pytest

from pytest_mock import MockerFixture
from typer.testing import CliRunner

from svs_core.__main__ import app


@pytest.mark.cli
class TestTemplateCommands:
    runner: CliRunner

    def setup_method(self) -> None:
        self.runner = CliRunner()

    def test_list_templates(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_template = mocker.MagicMock()
        mock_template.__str__.return_value = "Template(name='django')"
        mock_all.return_value = [mock_template]

        result = self.runner.invoke(
            app,
            ["template", "list"],
        )

        assert result.exit_code == 0
        assert "Template(name='django')" in result.output

    def test_list_templates_empty(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_all.return_value = []

        result = self.runner.invoke(
            app,
            ["template", "list"],
        )

        assert result.exit_code == 0
        assert "No templates found." in result.output

    def test_import_template_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mocker.patch("os.path.isfile", return_value=True)
        mock_open = mocker.patch(
            "builtins.open", mocker.mock_open(read_data='{"name": "test"}')
        )
        mock_load = mocker.patch("json.load")
        mock_load.return_value = {"name": "test"}

        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")
        mock_template = mocker.MagicMock()
        mock_template.name = "test"
        mock_import.return_value = mock_template

        result = self.runner.invoke(
            app,
            ["template", "import", "/path/to/template.json"],
        )

        assert result.exit_code == 0
        assert "Template 'test' imported successfully." in result.output

    def test_import_template_file_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mocker.patch("os.path.isfile", return_value=False)

        result = self.runner.invoke(
            app,
            ["template", "import", "/non/existent/file.json"],
        )

        assert result.exit_code == 1
        assert "File '/non/existent/file.json' does not exist." in result.output

    def test_delete_template_success(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.docker.template.Template.objects.get")
        mock_template = mocker.MagicMock()
        mock_get.return_value = mock_template

        result = self.runner.invoke(
            app,
            ["template", "delete", "1"],
        )

        assert result.exit_code == 0
        assert "✅ Template with ID '1' deleted successfully." in result.output
        mock_template.delete.assert_called_once()

    def test_delete_template_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mock_get = mocker.patch("svs_core.docker.template.Template.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            ["template", "delete", "999"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output
