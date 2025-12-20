import uuid

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from svs_core.docker.base import get_docker_client
from svs_core.docker.image import DockerImageManager


class TestDockerImageManager:
    @pytest.mark.integration
    def test_build_image_from_dockerfile(self) -> None:
        image_name = "svs-core-test-image:itest"
        dockerfile = """FROM busybox:latest
RUN echo 'hello from test' > /message
"""

        # Build image
        DockerImageManager.build_from_dockerfile(image_name, dockerfile)

        client = get_docker_client()
        images = client.images.list(name=image_name)
        assert any(
            image_name in (img.tags or []) for img in images
        ), "Built image tag not found locally"

        # Cleanup to avoid polluting local image cache
        client.images.remove(image=image_name, force=True)

    @pytest.mark.integration
    def test_build_invalid_dockerfile(self) -> None:
        image_name = "svs-core-test-image-invalid:fail"

        # Intentionally malformed instruction so Docker fails fast parsing
        invalid_dockerfile = "FRMO busybox:latest"  # typo in FROM

        with pytest.raises(Exception):  # docker-py may raise different exceptions
            DockerImageManager.build_from_dockerfile(image_name, invalid_dockerfile)

    @pytest.mark.integration
    def test_exists_nonexistent_image(self) -> None:
        random_tag = str(uuid.uuid4())
        assert not DockerImageManager.exists(f"svs-core-image-missing:{random_tag}")

    @pytest.mark.integration
    def test_exists_and_remove_image(self) -> None:
        tag = str(uuid.uuid4())[:8]
        image_name = f"svs-core-test-exists-remove:{tag}"
        dockerfile = """FROM busybox:latest\nRUN echo removed > /removed.txt\n"""

        DockerImageManager.build_from_dockerfile(image_name, dockerfile)
        try:
            assert DockerImageManager.exists(image_name)
        finally:
            # Ensure removal even if assertion fails later
            DockerImageManager.remove(image_name)

        assert not DockerImageManager.exists(image_name)

    @pytest.mark.integration
    def test_pull_image(self) -> None:
        image_name = "busybox:latest"
        # Pull (idempotent if already present)
        DockerImageManager.pull(image_name)
        assert DockerImageManager.exists(image_name)

        DockerImageManager.remove(image_name)

    @pytest.mark.integration
    def test_build_image_with_build_args(self) -> None:
        """Test building an image with build arguments."""
        image_name = "svs-core-test-build-args:test"
        dockerfile = """FROM busybox:latest
ARG TEST_ARG
ARG ANOTHER_ARG=default
RUN echo "TEST_ARG=${TEST_ARG}" > /test_arg.txt
RUN echo "ANOTHER_ARG=${ANOTHER_ARG}" > /another_arg.txt
"""
        build_args = {"TEST_ARG": "test_value", "ANOTHER_ARG": "custom_value"}

        # Build image with build args
        DockerImageManager.build_from_dockerfile(
            image_name, dockerfile, build_args=build_args
        )

        client = get_docker_client()
        images = client.images.list(name=image_name)
        assert any(
            image_name in (img.tags or []) for img in images
        ), "Built image with build args not found"

        # Verify build args were applied by running a container
        container = client.containers.run(
            image_name, command="cat /test_arg.txt", remove=True, detach=False
        )
        output = container.decode("utf-8").strip()
        assert "TEST_ARG=test_value" in output

        # Cleanup
        client.images.remove(image=image_name, force=True)

    @pytest.mark.integration
    def test_build_image_with_empty_build_args(self) -> None:
        """Test building an image with empty build_args (None)."""
        image_name = "svs-core-test-no-build-args:test"
        dockerfile = """FROM busybox:latest
ARG OPTIONAL_ARG=default_value
RUN echo "OPTIONAL_ARG=${OPTIONAL_ARG}" > /optional.txt
"""

        # Build image without build args (should use defaults)
        DockerImageManager.build_from_dockerfile(
            image_name, dockerfile, build_args=None
        )

        client = get_docker_client()
        images = client.images.list(name=image_name)
        assert any(
            image_name in (img.tags or []) for img in images
        ), "Built image without build args not found"

        # Verify default value was used
        container = client.containers.run(
            image_name, command="cat /optional.txt", remove=True, detach=False
        )
        output = container.decode("utf-8").strip()
        assert "OPTIONAL_ARG=default_value" in output

        # Cleanup
        client.images.remove(image=image_name, force=True)

    @pytest.mark.integration
    def test_remove_nonexistent_image_raises(self) -> None:
        random_tag = str(uuid.uuid4())
        image_name = f"svs-core-nonexistent-remove:{random_tag}"
        with pytest.raises(Exception):
            DockerImageManager.remove(image_name)

    @pytest.mark.integration
    def test_remove_image_with_containers_succeeds_with_force(self) -> None:
        """Test that remove succeeds even with running containers
        (force=True)."""
        tag = str(uuid.uuid4())[:8]
        image_name = f"svs-core-test-remove-in-use:{tag}"
        dockerfile = """FROM busybox:latest\nRUN echo in use > /in_use.txt\n"""

        DockerImageManager.build_from_dockerfile(image_name, dockerfile)

        client = get_docker_client()
        container = client.containers.run(image_name, command="sleep 60", detach=True)

        try:
            DockerImageManager.remove(image_name)
            assert not DockerImageManager.exists(image_name)
        finally:
            try:
                container.remove(force=True)
            except Exception:
                pass

    @pytest.mark.integration
    def test_remove_image_successfully(self) -> None:
        """Test successful removal of an image."""
        tag = str(uuid.uuid4())[:8]
        image_name = f"svs-core-test-remove-success:{tag}"
        dockerfile = """FROM busybox:latest
RUN echo 'test image' > /test.txt
"""

        DockerImageManager.build_from_dockerfile(image_name, dockerfile)

        assert DockerImageManager.exists(image_name)

        DockerImageManager.remove(image_name)

        assert not DockerImageManager.exists(image_name)
