"""Tests for custom exception hierarchy."""

import pytest

from svs_core.shared.exceptions import (
    AlreadyExistsException,
    ConfigurationException,
    DockerOperationException,
    InvalidOperationException,
    NotFoundException,
    ResourceException,
    ServiceOperationException,
    SVSException,
    TemplateException,
    ValidationException,
)


class TestExceptionHierarchy:
    """Test custom exception hierarchy and inheritance."""

    @pytest.mark.unit
    def test_svs_exception_is_base_exception(self) -> None:
        """Test that SVSException inherits from Exception."""
        assert issubclass(SVSException, Exception)

    @pytest.mark.unit
    def test_all_custom_exceptions_inherit_from_svs_exception(self) -> None:
        """Test that all custom exceptions inherit from SVSException."""
        exception_classes = [
            AlreadyExistsException,
            NotFoundException,
            InvalidOperationException,
            ValidationException,
            ConfigurationException,
            ServiceOperationException,
            TemplateException,
            DockerOperationException,
            ResourceException,
        ]

        for exc_class in exception_classes:
            assert issubclass(exc_class, SVSException)

    @pytest.mark.unit
    def test_already_exists_exception(self) -> None:
        """Test AlreadyExistsException initialization and message."""
        exc = AlreadyExistsException(entity="User", identifier="testuser")
        assert str(exc) == "User with identifier 'testuser' already exists."
        assert exc.entity == "User"
        assert exc.identifier == "testuser"

    @pytest.mark.unit
    def test_not_found_exception(self) -> None:
        """Test NotFoundException initialization and message."""
        exc = NotFoundException("Resource not found")
        assert str(exc) == "Resource not found"

    @pytest.mark.unit
    def test_invalid_operation_exception(self) -> None:
        """Test InvalidOperationException initialization and message."""
        exc = InvalidOperationException("Operation not allowed")
        assert str(exc) == "Operation not allowed"

    @pytest.mark.unit
    def test_validation_exception(self) -> None:
        """Test ValidationException initialization and message."""
        exc = ValidationException("Invalid input")
        assert str(exc) == "Invalid input"

    @pytest.mark.unit
    def test_configuration_exception(self) -> None:
        """Test ConfigurationException initialization and message."""
        exc = ConfigurationException("Invalid configuration")
        assert str(exc) == "Invalid configuration"

    @pytest.mark.unit
    def test_service_operation_exception(self) -> None:
        """Test ServiceOperationException initialization and message."""
        exc = ServiceOperationException("Service operation failed")
        assert str(exc) == "Service operation failed"

    @pytest.mark.unit
    def test_template_exception(self) -> None:
        """Test TemplateException initialization and message."""
        exc = TemplateException("Template error")
        assert str(exc) == "Template error"

    @pytest.mark.unit
    def test_docker_operation_exception(self) -> None:
        """Test DockerOperationException initialization and message."""
        exc = DockerOperationException("Docker operation failed")
        assert str(exc) == "Docker operation failed"

    @pytest.mark.unit
    def test_docker_operation_exception_with_chaining(self) -> None:
        """Test DockerOperationException with exception chaining."""
        original_error = ValueError("Docker API error")
        try:
            raise DockerOperationException(
                "Docker operation failed"
            ) from original_error
        except DockerOperationException as exc:
            assert str(exc) == "Docker operation failed"
            assert exc.__cause__ == original_error
            assert isinstance(exc.__cause__, ValueError)

    @pytest.mark.unit
    def test_resource_exception(self) -> None:
        """Test ResourceException initialization and message."""
        exc = ResourceException("No free resources")
        assert str(exc) == "No free resources"

    @pytest.mark.unit
    def test_exceptions_can_be_caught_as_svs_exception(self) -> None:
        """Test that all custom exceptions can be caught as SVSException."""
        with pytest.raises(SVSException):
            raise ValidationException("test")

        with pytest.raises(SVSException):
            raise ServiceOperationException("test")

        with pytest.raises(SVSException):
            raise DockerOperationException("test")

    @pytest.mark.unit
    def test_exceptions_can_be_caught_as_exception(self) -> None:
        """Test that all custom exceptions can be caught as Exception."""
        with pytest.raises(Exception):
            raise ValidationException("test")

        with pytest.raises(Exception):
            raise SVSException("test")
