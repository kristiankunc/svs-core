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
