from unittest import mock

import pytest
from pytest_mock import MockerFixture

from svs_core.docker.template import Template


@pytest.fixture(autouse=True)
def build_from_dockerfile_mock(mocker: MockerFixture) -> MockerFixture:
    return mocker.patch(
        "svs_core.docker.image.DockerImageManager.build_from_dockerfile",
        return_value=None,
    )


class TestTemplate:
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_and_get_by_id(self, build_from_dockerfile_mock):
        """Test creating a template and retrieving it by id."""
        name = "integration-template"
        dockerfile = "FROM busybox\n# NAME=integration-template\n# DESCRIPTION=Integration test\n# PROXY_PORTS=8080"
        description = "Integration test"
        exposed_ports = [8080]

        template = await Template.create(
            name=name,
            dockerfile=dockerfile,
            description=description,
            exposed_ports=exposed_ports,
        )
        assert template.name == name
        assert template.dockerfile == dockerfile
        assert template.description == description
        assert template.exposed_ports == exposed_ports
        build_from_dockerfile_mock.assert_called_once_with(
            dockerfile,
            name,
        )

        fetched = await Template.get_by_id(template.id)
        assert fetched is not None
        assert fetched.name == name
        assert fetched.dockerfile == dockerfile
        assert fetched.description == description
        assert fetched.exposed_ports == exposed_ports

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_create_valid_and_invalid(self, build_from_dockerfile_mock):
        """Test creating templates with valid and invalid parameters."""
        # Valid creation
        name = "unit-template"
        dockerfile = "FROM busybox\n# NAME=unit-template\n# DESCRIPTION=Unit test\n# PROXY_PORTS=1234,5678"
        description = "Unit test"
        exposed_ports = [1234, 5678]
        template = await Template.create(
            name=name,
            dockerfile=dockerfile,
            description=description,
            exposed_ports=exposed_ports,
        )
        assert template.name == name
        assert template.dockerfile == dockerfile
        assert template.description == description
        assert template.exposed_ports == exposed_ports
        build_from_dockerfile_mock.assert_called_once_with(
            dockerfile,
            name,
        )

        # Invalid: empty name
        with pytest.raises(ValueError):
            await Template.create(
                name="",
                dockerfile=dockerfile,
                description=description,
                exposed_ports=exposed_ports,
            )

        assert build_from_dockerfile_mock.call_count == 1

        # Invalid: empty dockerfile
        with pytest.raises(ValueError):
            await Template.create(
                name=name,
                dockerfile="",
                description=description,
                exposed_ports=exposed_ports,
            )

        assert build_from_dockerfile_mock.call_count == 1

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_import_from_url_success(
        self, monkeypatch, build_from_dockerfile_mock
    ):
        class FakeResponse:
            status_code = 200
            text = "FROM busybox\n# NAME=from-url\n# DESCRIPTION=From URL\n# PROXY_PORTS=8080,9090"

        async def fake_send_http_request(method, url):
            return FakeResponse()

        monkeypatch.setattr(
            "svs_core.docker.template.send_http_request", fake_send_http_request
        )

        template = await Template.import_from_url("http://fake-url/Dockerfile")
        assert template.name == "from-url"
        assert template.description == "From URL"
        assert template.exposed_ports == [8080, 9090]
        assert "# NAME=from-url" in template.dockerfile
        build_from_dockerfile_mock.assert_called_once_with(
            template.dockerfile,
            template.name,
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_import_from_url_failure(
        self, monkeypatch, build_from_dockerfile_mock
    ):
        class FakeResponse:
            status_code = 404
            text = ""

        async def fake_send_http_request(method, url):
            return FakeResponse()

        monkeypatch.setattr(
            "svs_core.docker.template.send_http_request", fake_send_http_request
        )

        with pytest.raises(ValueError):
            await Template.import_from_url("http://fake-url/Dockerfile")

        assert build_from_dockerfile_mock.call_count == 0

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_discover_from_github(self, monkeypatch, build_from_dockerfile_mock):
        class Repo:
            owner = "owner"
            name = "repo"
            path = ""

        directory_contents = [
            {
                "name": "my.Dockerfile",
                "download_url": "http://fake-url/my.Dockerfile",
            },
            {"name": "README.md", "download_url": "http://fake-url/README.md"},
        ]

        class DirResponse:
            def json(self):
                return directory_contents

        class FileResponse:
            text = "FROM busybox\n# NAME=github-template\n# DESCRIPTION=From GitHub\n# PROXY_PORTS=1234"

        async def fake_send_http_request(method, url):
            if url.startswith("https://api.github.com/repos/"):
                return DirResponse()
            if url == "http://fake-url/my.Dockerfile":
                return FileResponse()
            return mock.Mock(text="")

        monkeypatch.setattr(
            "svs_core.docker.template.destruct_github_url", lambda url: Repo()
        )
        monkeypatch.setattr(
            "svs_core.docker.template.send_http_request", fake_send_http_request
        )

        templates = await Template.discover_from_github("https://github.com/owner/repo")
        assert len(templates) == 1
        t = templates[0]
        assert t.name == "github-template"
        assert t.description == "From GitHub"
        assert t.exposed_ports == [1234]
        build_from_dockerfile_mock.assert_called_once_with(
            t.dockerfile,
            t.name,
        )

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_discover_from_github_no_dockerfile(
        self, monkeypatch, build_from_dockerfile_mock
    ):
        class Repo:
            owner = "owner"
            name = "repo"
            path = ""

        directory_contents = [
            {"name": "README.md", "download_url": "http://fake-url/README.md"}
        ]

        class DirResponse:
            def json(self):
                return directory_contents

        async def fake_send_http_request(method, url):
            return DirResponse()

        monkeypatch.setattr(
            "svs_core.docker.template.destruct_github_url", lambda url: Repo()
        )
        monkeypatch.setattr(
            "svs_core.docker.template.send_http_request", fake_send_http_request
        )

        templates = await Template.discover_from_github("https://github.com/owner/repo")
        assert templates == []
        assert build_from_dockerfile_mock.call_count == 0
