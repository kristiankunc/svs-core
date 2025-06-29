import pytest

from svs_core.docker.template import Template
from svs_core.shared.exceptions import AlreadyExistsException


class TestTemplate:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_and_get_by_name(self):
        """Test creating a template and retrieving it by name."""
        name = "integration-template"
        dockerfile = "FROM busybox\n# NAME=integration-template\n# DESCRIPTION=Integration test\n# PROXY_PORTS=8080"
        description = "Integration test"
        exposed_ports = [8080]

        # Clean up if exists
        existing = await Template.get_by_name(name)
        if existing:
            # Assuming a delete method exists, otherwise skip cleanup
            pass

        # Create
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

        # Get by name
        fetched = await Template.get_by_name(name)
        assert fetched is not None
        assert fetched.name == name
        assert fetched.dockerfile == dockerfile
        assert fetched.description == description
        assert fetched.exposed_ports == exposed_ports

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_create_duplicate_raises(self):
        """Test creating a duplicate template raises AlreadyExistsException."""
        name = "integration-duplicate"
        dockerfile = "FROM busybox\n# NAME=integration-duplicate"
        # Clean up if exists
        existing = await Template.get_by_name(name)
        if not existing:
            await Template.create(name=name, dockerfile=dockerfile)
        with pytest.raises(AlreadyExistsException):
            await Template.create(name=name, dockerfile=dockerfile)
