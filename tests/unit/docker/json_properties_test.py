import pytest

from svs_core.docker.json_properties import (
    DefaultContent,
    EnvVariable,
    ExposedPort,
    Healthcheck,
    KeyValue,
    Label,
    Volume,
)


@pytest.mark.unit
class TestKeyValue:
    """Tests for the KeyValue generic class."""

    def test_init(self):
        kv = KeyValue("k", "v")
        assert kv.key == "k" and kv.value == "v"

    def test_from_dict(self):
        kv = KeyValue.from_dict({"key": "k", "value": "v"})
        assert kv.to_dict() == {"key": "k", "value": "v"}

    def test_from_dict_invalid(self):
        with pytest.raises(ValueError):
            KeyValue.from_dict({"key": "k"})

    def test_array_operations(self):
        data = [{"key": "k1", "value": "v1"}]
        result = KeyValue.from_dict_array(data)
        assert KeyValue.to_dict_array(result) == data


@pytest.mark.unit
class TestEnvVariable:
    """Tests for the EnvVariable class."""

    def test_from_dict(self):
        env = EnvVariable.from_dict({"key": "DB_HOST", "value": "localhost"})
        assert env.key == "DB_HOST" and env.value == "localhost"

    def test_from_dict_invalid(self):
        with pytest.raises(ValueError):
            EnvVariable.from_dict({"KEY1": "v1", "KEY2": "v2"})

    def test_to_dict(self):
        assert EnvVariable("DEBUG", "true").to_dict() == {
            "key": "DEBUG",
            "value": "true",
        }


@pytest.mark.unit
class TestLabel:
    """Tests for the Label class."""

    def test_from_dict(self):
        label = Label.from_dict({"key": "app.name", "value": "myapp"})
        assert label.key == "app.name" and label.value == "myapp"

    def test_from_dict_invalid(self):
        with pytest.raises(ValueError):
            Label.from_dict({"label1": "v1", "label2": "v2"})

    def test_to_dict(self):
        result = Label("org.opencontainers.image.title", "MyApp").to_dict()
        assert result == {"key": "org.opencontainers.image.title", "value": "MyApp"}


@pytest.mark.unit
class TestExposedPort:
    """Tests for the ExposedPort class."""

    def test_init(self):
        port = ExposedPort(8000, 8080)
        assert port.container_port == 8080 and port.host_port == 8000

    def test_to_dict(self):
        assert ExposedPort(8000, 8080).to_dict() == {"key": 8000, "value": 8080}

    def test_setters(self):
        port = ExposedPort(8000, 8080)
        port.host_port = 9000
        port.container_port = 3000
        assert port.host_port == 9000 and port.container_port == 3000


@pytest.mark.unit
class TestVolume:
    """Tests for the Volume class."""

    def test_init(self):
        vol = Volume("/host/data", "/container/data")
        assert vol.container_path == "/container/data" and vol.host_path == "/host/data"

    def test_to_dict(self):
        vol = Volume("/host/data", "/container/data")
        assert vol.to_dict() == {"key": "/host/data", "value": "/container/data"}

    def test_setters(self):
        vol = Volume("/old/path", "/container/path")
        vol.host_path = "/new/path"
        vol.container_path = "/new/container"
        assert vol.host_path == "/new/path" and vol.container_path == "/new/container"


@pytest.mark.unit
class TestDefaultContent:
    """Tests for the DefaultContent class."""

    def test_init(self):
        content = DefaultContent("/etc/config.conf", "key=value")
        assert content.location == "/etc/config.conf" and content.content == "key=value"

    def test_to_dict(self):
        content = DefaultContent("/etc/config.conf", "key=value")
        assert content.to_dict() == {
            "key": "/etc/config.conf",
            "value": "key=value",
        }

    def test_from_dict(self):
        data = {"key": "/etc/config.conf", "value": "key=value"}
        content = DefaultContent.from_dict(data)
        assert content.location == "/etc/config.conf" and content.content == "key=value"

    def test_setters(self):
        content = DefaultContent("/old/path", "old content")
        content.location = "/new/path"
        content.content = "new content"
        assert content.location == "/new/path" and content.content == "new content"

    def test_str_long_content(self):
        long_content = "x" * 100
        content = DefaultContent("/etc/file", long_content)
        str_repr = str(content)
        assert "..." in str_repr
        assert "/etc/file" in str_repr

    def test_str_short_content(self):
        content = DefaultContent("/etc/file", "short")
        str_repr = str(content)
        assert "short" in str_repr
        assert "..." not in str_repr

    def test_write_to_host(self, tmp_path, mocker):
        """Test that write_to_host creates a file with the correct content."""
        # Mock run_command to avoid requiring actual system user
        mock_run = mocker.patch("svs_core.docker.json_properties.run_command")

        content = DefaultContent("/etc/config.conf", "key=value")
        host_file = tmp_path / "config.conf"

        content.write_to_host(str(host_file), username="testuser")

        # Verify run_command was called with correct parameters
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "key=value" in call_args[0][0]
        assert str(host_file) in call_args[0][0]


@pytest.mark.unit
class TestHealthcheck:
    """Tests for the Healthcheck class."""

    def test_init(self):
        hc = Healthcheck(test=["CMD", "curl"], interval=30)
        assert hc.test == ["CMD", "curl"] and hc.interval == 30

    def test_from_dict(self):
        hc = Healthcheck.from_dict({"test": ["CMD", "curl"], "interval": 30})
        assert hc is not None and hc.interval == 30

    def test_from_dict_empty(self):
        assert Healthcheck.from_dict(None) is None

    def test_from_dict_invalid(self):
        with pytest.raises((ValueError, TypeError)):
            Healthcheck.from_dict({"interval": 30})

    def test_to_dict(self):
        hc = Healthcheck(test=["CMD", "curl"], interval=30)
        result = hc.to_dict()
        assert result == {"test": ["CMD", "curl"], "interval": 30}
