from docker.models.images import Image as DockerImage

from svs_core.docker.base import get_docker_client


class DockerImageManager:
    @staticmethod
    def get_images() -> list[DockerImage]:
        """
        Retrieves a list of Docker images.

        Returns:
            list: A list of Docker image objects.
        """
        return get_docker_client().images.list()  # type: ignore

    @staticmethod
    def pull_image(image_name: str) -> None:
        """
        Pulls a Docker image from a registry.

        Args:
            image_name (str): The name of the image to pull.

        Raises:
            docker.errors.APIError: If the image pull fails.
        """
        get_docker_client().images.pull(image_name)

    @staticmethod
    def remove_image(image_name: str) -> None:
        """
        Removes a Docker image by its name.

        Args:
            image_name (str): The name of the image to remove.

        Raises:
            docker.errors.APIError: If the image removal fails.
        """
        image = get_docker_client().images.get(image_name)
        get_docker_client().images.remove(image.id)

    @staticmethod
    def build_image(dockerfile_path: str, tag: str) -> DockerImage:
        """
        Builds a Docker image from a Dockerfile.

        Args:
            dockerfile_path (str): The path to the Dockerfile.
            tag (str): The tag for the built image.

        Returns:
            DockerImage: The built Docker image object.

        Raises:
            docker.errors.BuildError: If the image build fails.
        """
        return get_docker_client().images.build(path=dockerfile_path, tag=tag)[0]
