import pytest

from svs_core.migrations.migrator import PackageVersion


@pytest.mark.unit
class TestPackageVersion:
    """Test suite for PackageVersion dataclass."""

    @pytest.mark.parametrize(
        "version_str,expected_major,expected_minor,expected_patch",
        [
            ("1.2.3", 1, 2, 3),
            ("0.0.0", 0, 0, 0),
            ("100.200.300", 100, 200, 300),
            ("01.02.03", 1, 2, 3),
            ("-1.2.3", -1, 2, 3),
        ],
    )
    def test_parse_valid_version(
        self,
        version_str: str,
        expected_major: int,
        expected_minor: int,
        expected_patch: int,
    ) -> None:
        """Test version parsing with valid major.minor.patch formats."""
        pv = PackageVersion(version_str)
        assert pv.string == version_str
        assert pv.major == expected_major
        assert pv.minor == expected_minor
        assert pv.patch == expected_patch

    @pytest.mark.parametrize(
        "invalid_version",
        [
            "2.5",
            "3",
            "",
            "a.2.3",
            "1.b.3",
            "1.2.c",
            "1.2.3.4.5",
            "1.invalid.3",
        ],
    )
    def test_parse_invalid_version_raises_error(self, invalid_version: str) -> None:
        """Test that invalid version formats raise ValueError."""
        with pytest.raises(ValueError, match="Invalid version format"):
            PackageVersion(invalid_version)

    def test_as_tuple(self) -> None:
        """Test that version is correctly converted to comparison tuple."""
        pv = PackageVersion("1.2.3")
        assert pv._as_tuple() == (1, 2, 3)

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("1.0.0", "2.0.0", True),  # major difference
            ("1.2.0", "1.3.0", True),  # minor difference
            ("1.2.3", "1.2.4", True),  # patch difference
            ("2.0.0", "1.0.0", False),  # v1 greater
            ("1.0.0", "1.0.0", False),  # equal
        ],
    )
    def test_less_than(self, v1: str, v2: str, expected: bool) -> None:
        """Test less than comparison operator."""
        pv1 = PackageVersion(v1)
        pv2 = PackageVersion(v2)
        assert (pv1 < pv2) == expected

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("1.0.0", "2.0.0", True),  # v1 less than v2
            ("1.0.0", "1.0.0", True),  # equal
            ("2.0.0", "1.0.0", False),  # v1 greater
        ],
    )
    def test_less_than_or_equal(self, v1: str, v2: str, expected: bool) -> None:
        """Test less than or equal comparison operator."""
        pv1 = PackageVersion(v1)
        pv2 = PackageVersion(v2)
        assert (pv1 <= pv2) == expected

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("2.0.0", "1.0.0", True),  # major difference
            ("1.3.0", "1.2.0", True),  # minor difference
            ("1.2.4", "1.2.3", True),  # patch difference
            ("1.0.0", "2.0.0", False),  # v1 less
            ("1.0.0", "1.0.0", False),  # equal
        ],
    )
    def test_greater_than(self, v1: str, v2: str, expected: bool) -> None:
        """Test greater than comparison operator."""
        pv1 = PackageVersion(v1)
        pv2 = PackageVersion(v2)
        assert (pv1 > pv2) == expected

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("2.0.0", "1.0.0", True),  # v1 greater than v2
            ("1.0.0", "1.0.0", True),  # equal
            ("1.0.0", "2.0.0", False),  # v1 less
        ],
    )
    def test_greater_than_or_equal(self, v1: str, v2: str, expected: bool) -> None:
        """Test greater than or equal comparison operator."""
        pv1 = PackageVersion(v1)
        pv2 = PackageVersion(v2)
        assert (pv1 >= pv2) == expected

    @pytest.mark.parametrize(
        "v1,v2,expected",
        [
            ("1.0.0", "1.0.0", True),
            ("1.2.3", "1.2.3", True),
            ("0.0.0", "0.0.0", True),
            ("1.0.0", "1.0.1", False),
            ("1.0.0", "1.1.0", False),
            ("1.0.0", "2.0.0", False),
        ],
    )
    def test_equality(self, v1: str, v2: str, expected: bool) -> None:
        """Test equality comparison operator."""
        pv1 = PackageVersion(v1)
        pv2 = PackageVersion(v2)
        assert (pv1 == pv2) == expected

    def test_comparison_chain(self) -> None:
        """Test chaining multiple version comparisons."""
        v1 = PackageVersion("1.0.0")
        v2 = PackageVersion("1.5.0")
        v3 = PackageVersion("2.0.0")

        assert v1 < v2 < v3
        assert v3 > v2 > v1
        assert v1 <= v2 <= v3
