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
        """Test the _merge_overrides method with Label items."""
        base = [Label(key="A", value="1"), Label(key="B", value="2")]
        overrides = [Label(key="B", value="3"), Label(key="C", value="4")]

        result = Service._merge_overrides(base, overrides)

        # Verify result has correct length
        assert len(result) == 3

        result_dict = {item.key: item.value for item in result}
        assert result_dict["A"] == "1"
        assert result_dict["B"] == "3"  # Overridden
        assert result_dict["C"] == "4"

    @pytest.mark.unit
    def test_merge_overrides_with_env_variables(self):
        """Test the _merge_overrides method with EnvVariable items."""
        base = [
            EnvVariable(key="A", value="1"),
            EnvVariable(key="B", value="2"),
        ]
        overrides = [
            EnvVariable(key="B", value="3"),
            EnvVariable(key="C", value="4"),
        ]

        result = Service._merge_overrides(base, overrides)

        # Verify result has correct length
        assert len(result) == 3

        result_dict = {item.key: item.value for item in result}
        assert result_dict["A"] == "1"
        assert result_dict["B"] == "3"  # Overridden
        assert result_dict["C"] == "4"

    @pytest.mark.unit
    def test_merge_overrides_with_volumes(self):
        """Test the _merge_overrides method with Volume items.

        Volumes are now identified by container_path (key) rather than
        host_path (value), so overrides correctly replace volumes with
        the same container mount point.
        """
        # Create volumes with container paths as identifiers
        base = [
            Volume(host_path="A", container_path="1"),
            Volume(host_path="B", container_path="2"),
        ]
        overrides = [
            # Different container path
            Volume(host_path="B", container_path="3"),
            # Same container path as base[0]
            Volume(host_path="override", container_path="1"),
        ]

        result = Service._merge_overrides(base, overrides)

        # Verify result has correct length (override matching container path 1, original 2, new 3)
        assert len(result) == 3

        # Convert to dict using container_path as key for easier verification
        result_dict = {item.container_path: item.host_path for item in result}
        assert result_dict["1"] == "override"  # Overridden
        assert result_dict["2"] == "B"  # Original
        assert result_dict["3"] == "B"  # New
