import json

from pathlib import Path

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
        mock_template.id = "1"
        mock_template.name = "django"
        mock_template.type = "web"
        mock_template.description = "Django web framework"
        mock_template.docs_url = None
        mock_all.return_value = [mock_template]

        result = self.runner.invoke(
            app,
            ["template", "list"],
        )

        assert result.exit_code == 0
        # Table output should contain template name and type
        assert "django" in result.output
        assert "web" in result.output

    def test_list_templates_empty(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_all.return_value = []

        result = self.runner.invoke(
            app,
            ["template", "list"],
        )

        assert result.exit_code == 0
        assert "No templates found." in result.output

    def test_list_templates_inline(self, mocker: MockerFixture) -> None:
        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_template = mocker.MagicMock()
        mock_template.__str__.return_value = "Template(name='django')"
        mock_all.return_value = [mock_template]

        result = self.runner.invoke(
            app,
            ["template", "list", "--inline"],
        )

        assert result.exit_code == 0
        assert "Template(name='django')" in result.output

    def test_import_template_success(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")

        # Create a temporary JSON file
        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps({"name": "test", "type": "web"}))

        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_all.return_value = []

        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")
        mock_template = mocker.MagicMock()
        mock_template.name = "test"
        mock_import.return_value = mock_template

        result = self.runner.invoke(
            app,
            ["template", "import", str(template_file)],
        )

        assert result.exit_code == 0
        assert "Template 'test' imported successfully." in result.output

    def test_import_template_file_not_found(self, mocker: MockerFixture) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mocker.patch("os.path.exists", return_value=False)

        result = self.runner.invoke(
            app,
            ["template", "import", "/non/existent/file.json"],
        )

        assert result.exit_code == 1
        assert (
            "File/directory '/non/existent/file.json' does not exist." in result.output
        )

    def test_import_template_recursive_not_directory(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")
        mocker.patch("os.path.exists", return_value=True)
        mocker.patch("os.path.isdir", return_value=False)

        result = self.runner.invoke(
            app,
            ["template", "import", "/path/to/file.json", "-r"],
        )

        assert result.exit_code == 1
        assert "is not a directory for recursive import" in result.output

    def test_import_template_skip_existing(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")

        # Create a temporary JSON file
        template_file = tmp_path / "template.json"
        template_file.write_text(json.dumps({"name": "existing", "type": "web"}))

        mock_existing = mocker.MagicMock()
        mock_existing.name = "existing"
        mock_existing.type = "web"
        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_all.return_value = [mock_existing]

        mock_confirm = mocker.patch("svs_core.cli.template.confirm_action")
        mock_confirm.return_value = True

        result = self.runner.invoke(
            app,
            ["template", "import", str(template_file)],
        )

        assert result.exit_code == 0
        assert "Skipping import of template 'existing'." in result.output

    def test_import_template_recursive_success(
        self, mocker: MockerFixture, tmp_path: Path
    ) -> None:
        mocker.patch("svs_core.cli.template.reject_if_not_admin")

        # Create temporary JSON files
        (tmp_path / "template1.json").write_text(
            json.dumps({"name": "template1", "type": "web"})
        )
        (tmp_path / "template2.json").write_text(
            json.dumps({"name": "template2", "type": "db"})
        )
        (tmp_path / "schema.json").write_text(json.dumps({"type": "object"}))

        mock_all = mocker.patch("svs_core.docker.template.Template.objects.all")
        mock_all.return_value = []

        mock_import = mocker.patch("svs_core.docker.template.Template.import_from_json")
        mock_template1 = mocker.MagicMock()
        mock_template1.name = "template1"
        mock_template2 = mocker.MagicMock()
        mock_template2.name = "template2"
        mock_import.side_effect = [mock_template1, mock_template2]

        result = self.runner.invoke(
            app,
            ["template", "import", str(tmp_path), "-r"],
        )

        assert result.exit_code == 0
        assert "template1" in result.output
        assert "template2" in result.output
        # schema.json should be filtered out
        assert mock_import.call_count == 2

    def test_get_template_success(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.template.Template.objects.get")
        mock_template = mocker.MagicMock()
        mock_template.pprint.return_value = "Template(name='django')"
        mock_get.return_value = mock_template

        result = self.runner.invoke(
            app,
            ["template", "get", "1"],
        )

        assert result.exit_code == 0
        assert "Template(name='django')" in result.output
        mock_get.assert_called_once_with(id="1")

    def test_get_template_long_format(self, mocker: MockerFixture) -> None:
        mock_get = mocker.patch("svs_core.docker.template.Template.objects.get")
        mock_template = mocker.MagicMock()
        mock_template.name = "django"
        mock_template.id = 1
        mock_template.type = "image"
        mock_template.__str__.return_value = (
            "name=django\n"
            "id=1\n"
            "type=image\n"
            "image=django:latest\n"
            "dockerfile_head=[]\n"
            "description=Django web framework\n"
            "default_env=[]\n"
            "default_ports=[]\n"
            "default_volumes=[]\n"
            "default_contents=[]\n"
            "start_cmd=None\n"
            "healthcheck=None\n"
            "labels=[]\n"
            "args=[]"
        )
        mock_get.return_value = mock_template

        result = self.runner.invoke(
            app,
            ["template", "get", "1", "--long"],
        )

        assert result.exit_code == 0
        assert "name=django" in result.output
        assert "id=1" in result.output
        assert "type=image" in result.output
        assert "image=django:latest" in result.output
        assert "description=Django web framework" in result.output
        assert "default_env=[]" in result.output
        assert "default_ports=[]" in result.output
        assert "default_volumes=[]" in result.output

    def test_get_template_not_found(self, mocker: MockerFixture) -> None:
        from django.core.exceptions import ObjectDoesNotExist

        mock_get = mocker.patch("svs_core.docker.template.Template.objects.get")
        mock_get.side_effect = ObjectDoesNotExist()

        result = self.runner.invoke(
            app,
            ["template", "get", "999"],
        )

        assert result.exit_code == 1
        assert "not found" in result.output

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
        assert "Template with ID '1' deleted successfully." in result.output
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
