from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from svs_core.docker.template import Template


class TestUnitDockerTemplate:
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch("svs_core.docker.template.send_http_request")
    @patch.object(Template, "create", new_callable=AsyncMock)
    async def test_import_from_url_success(self, mock_create, mock_send_http_request):
        """Test importing a Dockerfile from a URL successfully."""

        dockerfile_content = "# NAME=test\n# DESCRIPTION=desc\n# PROXY_PORTS=8080,443"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = dockerfile_content
        mock_send_http_request.return_value = mock_response

        mock_create.return_value = "template_obj"

        await Template.import_from_url("http://example.com/Dockerfile")
        mock_create.assert_awaited_once_with(
            name="test",
            dockerfile=dockerfile_content,
            description="desc",
            exposed_ports=[8080, 443],
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch("svs_core.docker.template.send_http_request")
    async def test_import_from_url_failure(self, mock_send_http_request):
        """Test importing a Dockerfile from a URL that fails."""

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_send_http_request.return_value = mock_response

        with pytest.raises(ValueError, match="Failed to fetch Dockerfile"):
            await Template.import_from_url("http://example.com/Dockerfile")

    @pytest.mark.unit
    @patch("svs_core.docker.template.send_http_request")
    @patch.object(Template, "create", new_callable=AsyncMock)
    def test_discover_from_github(self, mock_create, mock_send_http_request):
        """Test discovering a template from a GitHub repository."""

        directory_contents = [
            {
                "name": "my.Dockerfile",
                "download_url": "http://example.com/my.Dockerfile",
            },
            {"name": "README.md", "download_url": "http://example.com/README.md"},
        ]
        dockerfile_content = "# NAME=web\n# DESCRIPTION=webdesc\n# PROXY_PORTS=80"

        mock_response_dir = MagicMock()
        mock_response_dir.json.return_value = directory_contents
        mock_response_file = MagicMock()
        mock_response_file.text = dockerfile_content

        mock_send_http_request.side_effect = [mock_response_dir, mock_response_file]
        mock_create.return_value = "template_obj"

        with patch("svs_core.docker.template.destruct_github_url") as mock_destruct:
            mock_destruct.return_value = MagicMock(
                owner="owner", name="repo", path=None
            )
            import asyncio

            asyncio.run(Template.discover_from_github("https://github.com/owner/repo"))
            mock_create.assert_awaited_once_with(
                name="web",
                dockerfile=dockerfile_content,
                description="webdesc",
                exposed_ports=[80],
            )

    @pytest.mark.unit
    @patch("svs_core.docker.template.send_http_request")
    def test_discover_from_github_no_dockerfile(self, mock_send_http_request):
        """Test discovering a template from a GitHub repository with no Dockerfile."""

        directory_contents = [
            {"name": "README.md", "download_url": "http://example.com/README.md"}
        ]
        mock_response_dir = MagicMock()
        mock_response_dir.json.return_value = directory_contents
        mock_send_http_request.return_value = mock_response_dir

        with patch("svs_core.docker.template.destruct_github_url") as mock_destruct:
            mock_destruct.return_value = MagicMock(
                owner="owner", name="repo", path=None
            )
            import asyncio

            result = asyncio.run(
                Template.discover_from_github("https://github.com/owner/repo")
            )
            assert result == []
