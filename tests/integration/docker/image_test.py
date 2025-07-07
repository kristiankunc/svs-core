import uuid

import docker
import pytest

from svs_core.docker.base import get_docker_client
from svs_core.docker.image import DockerImageManager


class TestDockerImageManager:
    @pytest.mark.integration
    def test_get_images(self):
        """Tests retrieving a list of Docker images."""

        images = DockerImageManager.get_images()
        assert isinstance(images, list)
        assert all(hasattr(img, "id") for img in images)

    @pytest.mark.integration
    def test_pull_and_remove_image(self):
        """Tests pulling and removing a Docker image."""

        image_name = "hello-world:latest"

        client = get_docker_client()
        try:
            client.images.remove(image_name, force=True)
        except docker.errors.ImageNotFound:
            pass

        DockerImageManager.pull_image(image_name)
        images = DockerImageManager.get_images()
        assert any(image_name in tag for img in images for tag in img.tags)

        DockerImageManager.remove_image(image_name)
        images = DockerImageManager.get_images()
        assert not any(image_name in tag for img in images for tag in img.tags)

    @pytest.mark.integration
    def test_build_image(self, tmp_path):
        """Tests building a Docker image from a Dockerfile."""

        dockerfile = tmp_path / "Dockerfile"
        dockerfile.write_text('FROM alpine:latest\nCMD ["echo", "hello"]\n')
        tag = f"test-image:{uuid.uuid4().hex[:8]}"

        image = DockerImageManager.build_image(str(tmp_path), tag)
        assert image is not None
        assert tag in image.tags[0]

        DockerImageManager.remove_image(tag)
