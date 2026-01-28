import os
import shutil
import tempfile

from pathlib import Path

from docker.errors import APIError, BuildError
from docker.models.images import Image

from svs_core.docker.base import get_docker_client
from svs_core.shared.exceptions import DockerOperationException
from svs_core.shared.logger import get_logger


class DockerImageManager:
    """Class for managing Docker images."""

    @staticmethod
    def build_from_dockerfile(
        image_name: str,
        dockerfile_content: str,
        path_to_copy: Path | None = None,
        build_args: dict[str, str] | None = None,
    ) -> None:
        """Build a Docker image from an in-memory Dockerfile.

        Args:
            image_name (str): Name of the image.
            dockerfile_content (str): Dockerfile contents.
            path_to_copy (Path | None): Optional path to copy into the build context.
            build_args (dict[str, str] | None): Optional build arguments to pass to Docker.

        Raises:
            DockerOperationException: If the Docker build fails. On failure, a detailed error log is written to
                `<path_to_copy>/docker_build_error.log` (or `./docker_build_error.log` if path_to_copy
                is not provided) containing the image name, error message, and full build log output.
        """
        get_logger(__name__).info(
            f"Building Docker image '{image_name}' from Dockerfile"
        )
        get_logger(__name__).debug(
            f"Build context path: {path_to_copy if path_to_copy else 'None'}"
        )

        client = get_docker_client()

        with tempfile.TemporaryDirectory() as tmpdir:
            dockerfile_path = os.path.join(tmpdir, "Dockerfile")
            with open(dockerfile_path, "w", encoding="utf-8") as f:
                f.write(dockerfile_content)

            if path_to_copy:
                if path_to_copy.is_dir():
                    for item in path_to_copy.iterdir():
                        target = Path(tmpdir) / item.name
                        if item.is_dir():
                            shutil.copytree(item, target)
                        else:
                            shutil.copy2(item, target)
                else:
                    shutil.copy2(path_to_copy, Path(tmpdir) / path_to_copy.name)

            try:
                client.images.build(
                    path=tmpdir,
                    tag=image_name,
                    rm=True,
                    forcerm=True,
                    labels={"svs": "true"},
                    buildargs=build_args,
                )
                get_logger(__name__).info(
                    f"Successfully built Docker image '{image_name}'"
                )
            except (BuildError, APIError) as e:
                logger = get_logger(__name__)

                # Parse build log from the exception
                build_log_lines = []
                if hasattr(e, "build_log") and e.build_log:
                    for line in e.build_log:
                        if isinstance(line, bytes):
                            build_log_lines.append(
                                line.decode("utf-8", errors="replace")
                            )
                        elif isinstance(line, str):
                            build_log_lines.append(line)
                        elif isinstance(line, dict):
                            # Docker API sometimes returns JSON objects
                            if "stream" in line:
                                build_log_lines.append(line["stream"].rstrip())
                            elif "error" in line:
                                build_log_lines.append(f"ERROR: {line['error']}")
                            else:
                                build_log_lines.append(str(line))
                        else:
                            build_log_lines.append(str(line))

                build_log = "\n".join(build_log_lines)

                # Log the error message immediately
                error_msg = str(e)
                logger.error(f"Docker build failed: {error_msg}")

                # Log the full build output
                if build_log:
                    logger.error(f"Build log output:\n{build_log}")

                # Write detailed log file
                if path_to_copy:
                    log_path = Path(path_to_copy) / "docker_build_error.log"
                else:
                    log_path = Path.cwd() / "docker_build_error.log"

                try:
                    with open(log_path, "w", encoding="utf-8") as log_file:
                        log_file.write(f"Docker Build Error\n")
                        log_file.write(f"==================\n\n")
                        log_file.write(f"Image: {image_name}\n")
                        log_file.write(f"Error: {error_msg}\n\n")
                        log_file.write(f"Build Log:\n")
                        log_file.write(f"-----------\n")
                        log_file.write(build_log)

                    error_with_log_path = (
                        f"{error_msg}\n\nDetailed error log written to: {log_path}"
                    )
                    logger.error(
                        f"Failed to build image '{image_name}'. {error_with_log_path}"
                    )
                    raise DockerOperationException(error_with_log_path) from e
                except DockerOperationException:
                    raise
                except Exception as log_write_error:
                    logger.error(
                        f"Failed to write error log to {log_path}: {str(log_write_error)}"
                    )
                    raise

    @staticmethod
    def exists(image_name: str) -> bool:
        """Check if a Docker image exists locally.

        Args:
            image_name (str): Name of the image.

        Returns:
            bool: True if the image exists, False otherwise.
        """
        get_logger(__name__).debug(f"Checking if image '{image_name}' exists locally")

        client = get_docker_client()
        try:
            client.images.get(image_name)
            get_logger(__name__).debug(f"Image '{image_name}' found locally")
            return True
        except Exception:
            get_logger(__name__).debug(f"Image '{image_name}' not found locally")
            return False

    @staticmethod
    def remove(image_name: str) -> None:
        """Remove a Docker image from the local system.

        Args:
            image_name (str): Name of the image.

        Raises:
            DockerOperationException: If the image cannot be removed.
        """
        get_logger(__name__).debug(f"Removing image '{image_name}'")

        client = get_docker_client()

        try:
            client.images.remove(image_name, force=True)
            get_logger(__name__).info(f"Successfully removed image '{image_name}'")
        except Exception as e:
            get_logger(__name__).error(
                f"Failed to remove image '{image_name}': {str(e)}"
            )
            raise DockerOperationException(
                f"Failed to remove image {image_name}. Error: {str(e)}"
            ) from e

    @staticmethod
    def pull(image_name: str) -> None:
        """Pull a Docker image from a registry.

        Args:
            image_name (str): Name of the image.

        Raises:
            DockerOperationException: If the image cannot be pulled.
        """
        get_logger(__name__).info(f"Pulling Docker image '{image_name}' from registry")

        client = get_docker_client()

        try:
            client.images.pull(f"{image_name}")
            get_logger(__name__).info(f"Successfully pulled image '{image_name}'")
        except Exception as e:
            get_logger(__name__).error(f"Failed to pull image '{image_name}': {str(e)}")
            raise DockerOperationException(
                f"Failed to pull image {image_name}. Error: {str(e)}"
            ) from e

    @staticmethod
    def get_all() -> list[Image]:
        """Get a list of all local Docker images.

        Returns:
            list[Image]: List of Docker Image objects.
        """
        client = get_docker_client()
        return client.images.list()  # type: ignore

    @staticmethod
    def delete(image_name: str) -> None:
        """Delete a Docker image by name.

        Args:
            image_name (str): Name of the image to delete.
        """
        DockerImageManager.remove(image_name)

    @staticmethod
    def rename(old_name: str, new_name: str) -> None:
        """Rename a Docker image.

        Args:
            old_name (str): Current name of the image.
            new_name (str): New name for the image.

        Raises:
            DockerOperationException: If the image cannot be renamed.
        """
        logger = get_logger(__name__)
        logger.debug(f"Renaming image from '{old_name}' to '{new_name}'")

        client = get_docker_client()
        try:
            image = client.images.get(old_name)
        except Exception as e:
            logger.error(
                f"Failed to find image '{old_name}' for renaming to '{new_name}': {str(e)}"
            )
            raise DockerOperationException(
                f"Failed to rename image '{old_name}' to '{new_name}': source image not found or inaccessible. Error: {str(e)}"
            ) from e

        try:
            image.tag(new_name)
            logger.info(f"Tagged image '{old_name}' as '{new_name}'")
        except Exception as e:
            logger.error(f"Failed to tag image '{old_name}' as '{new_name}': {str(e)}")
            raise DockerOperationException(
                f"Failed to rename image '{old_name}' to '{new_name}': tagging failed. Error: {str(e)}"
            ) from e

        try:
            DockerImageManager.remove(old_name)
        except Exception as e:
            # The new tag exists, but cleanup of the old tag failed.
            logger.warning(
                f"Image '{new_name}' created, but failed to remove old image '{old_name}': {str(e)}"
            )
