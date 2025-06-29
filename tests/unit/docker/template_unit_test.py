from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from svs_core.docker.template import Template


class DummyModel:
    def __init__(self, name, dockerfile, description=None, exposed_ports=None):
        self.name = name
        self.dockerfile = dockerfile
        self.description = description
        self.exposed_ports = exposed_ports

    async def create(self):
        pass


class TestTemplateClassMethods:
    @pytest.mark.asyncio
    @patch("svs_core.docker.template.Template._exists", new_callable=AsyncMock)
    @patch("svs_core.docker.template.TemplateModel")
    async def test_create_success(self, mock_model_cls, mock_exists):
        """Test creating a new template successfully."""
        mock_exists.return_value = False
        mock_model = MagicMock()
        mock_model.create = AsyncMock()
        mock_model_cls.return_value = mock_model
        t = await Template.create(
            name="Test", dockerfile="FROM test", description="desc", exposed_ports=[123]
        )
        assert t._model == mock_model
        mock_exists.assert_awaited_once_with("name", "test")
        mock_model_cls.assert_called_once_with(
            name="test",
            dockerfile="FROM test",
            description="desc",
            exposed_ports=[123],
        )
        mock_model.create.assert_awaited_once()

    @pytest.mark.asyncio
    @patch("svs_core.docker.template.Template._get", new_callable=AsyncMock)
    async def test_get_by_name(self, mock_get):
        """Test retrieving a template by name."""
        mock_get.return_value = MagicMock(spec=Template)
        res = await Template.get_by_name("TestName ")
        assert res == mock_get.return_value
        mock_get.assert_awaited_once_with("name", "testname")

    @pytest.mark.asyncio
    @patch("svs_core.docker.template.send_http_request", new_callable=AsyncMock)
    @patch("svs_core.docker.template.destruct_github_url")
    @patch("svs_core.docker.template.Template.create", new_callable=AsyncMock)
    async def test_discover_from_github(self, mock_create, mock_destruct, mock_http):
        """Test discovering templates from a GitHub repository."""
        # Setup fake repo and response
        mock_destruct.return_value = MagicMock(owner="foo", name="bar", path=None)
        mock_http.side_effect = [
            MagicMock(
                json=MagicMock(
                    return_value=[{"name": "my.Dockerfile", "download_url": "url"}]
                )
            ),
            MagicMock(
                text="# NAME=abc\n# DESCRIPTION=desc\n# PROXY_PORTS=8080,443\nFROM test"
            ),
        ]
        mock_create.return_value = MagicMock(spec=Template, name="abc")
        templates = await Template.discover_from_github("https://github.com/foo/bar")
        assert [t.name for t in templates] == ["abc"]
        mock_create.assert_awaited_once_with(
            name="abc",
            dockerfile="# NAME=abc\n# DESCRIPTION=desc\n# PROXY_PORTS=8080,443\nFROM test",
            description="desc",
            exposed_ports=[8080, 443],
        )
