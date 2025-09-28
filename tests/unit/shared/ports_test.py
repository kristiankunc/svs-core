from types import SimpleNamespace

import pytest

from svs_core.shared.ports import SystemPortManager


class TestSystemPortManager:
    def test_is_port_used_true(self, monkeypatch):
        """Simulate that the port is used by mocking run_command to returncode 0."""
        monkeypatch.setattr(
            "svs_core.shared.ports.run_command",
            lambda cmd, check=True: SimpleNamespace(returncode=0),
        )

        assert SystemPortManager.is_port_used(12345) is True

    def test_is_port_used_false(self, monkeypatch):
        """Simulate that the port is not used by mocking run_command to returncode 1."""
        monkeypatch.setattr(
            "svs_core.shared.ports.run_command",
            lambda cmd, check=True: SimpleNamespace(returncode=1),
        )

        assert SystemPortManager.is_port_used(12345) is False

    def test_find_free_port_returns_port_when_available(self, monkeypatch):
        """Test that find_free_port returns a port when one is available."""

        monkeypatch.setattr("svs_core.shared.ports.random.choice", lambda rng: 50000)
        monkeypatch.setattr(
            "svs_core.shared.ports.SystemPortManager.is_port_used",
            staticmethod(lambda port: False),
        )

        port = SystemPortManager.find_free_port()
        assert isinstance(port, int)
        assert port == 50000

    def test_find_free_port_raises_after_max_attempts(self, monkeypatch):
        """Test that find_free_port raises RuntimeError after maximum attempts."""

        monkeypatch.setattr(
            "svs_core.shared.ports.SystemPortManager.is_port_used",
            staticmethod(lambda port: True),
        )

        with pytest.raises(RuntimeError):
            SystemPortManager.find_free_port()
