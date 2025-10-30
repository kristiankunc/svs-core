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
    @pytest.mark.parametrize(
        "make_kv",
        [
            lambda k, v: Label(key=k, value=v),
            lambda k, v: EnvVariable(key=k, value=v),
            lambda k, v: ExposedPort(host_port=k, container_port=v),
            lambda k, v: Volume(host_path=k, container_path=v),
        ],
    )
    def test_merge_overrides(self, make_kv):
        """Test the _merge_overrides static method for all KeyValue
        subclasses."""
        base = [make_kv("A", "1"), make_kv("B", "2")]
        overrides = [make_kv("B", "3"), make_kv("C", "4")]

        result = Service._merge_overrides(base, overrides)

        # Verify result has correct length
        assert len(result) == 3

        # Sort by key for consistent comparison
        result_sorted = sorted(result, key=lambda x: x.key)

        assert result_sorted[0].key == "A"
        assert result_sorted[0].value == "1"

        assert result_sorted[1].key == "B"
        assert result_sorted[1].value == "3"

        assert result_sorted[2].key == "C"
        assert result_sorted[2].value == "4"
