import pytest

from svs_core.docker.json_properties import (
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
