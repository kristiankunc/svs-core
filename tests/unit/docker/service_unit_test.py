import pytest

from pytest_mock import MockerFixture

from svs_core.docker.json_properties import (
    EnvVariable,
    ExposedPort,
    Label,
    Volume,
)
from svs_core.docker.service import Service


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
        with pytest.raises(ValueError, match="Domain must be a string"):
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
