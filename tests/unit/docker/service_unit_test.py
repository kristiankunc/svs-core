import pytest

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
