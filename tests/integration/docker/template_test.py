import pytest
from tortoise.contrib.test import TestCase

from svs_core.docker.template import Template


class TestTemplate(TestCase):
    @pytest.mark.integration
    async def test_create_and_get_by_id(self):
        """Test creating a template and retrieving it by id."""
        name = "integration-template"
        dockerfile = "FROM busybox\n# NAME=integration-template\n# DESCRIPTION=Integration test\n# PROXY_PORTS=8080"
        description = "Integration test"
        exposed_ports = [8080]

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

        fetched = await Template.get_by_id(template.id)

        assert fetched is not None
        assert fetched.name == name
        assert fetched.dockerfile == dockerfile
        assert fetched.description == description
        assert fetched.exposed_ports == exposed_ports
