"""Unit tests for TUI CLI functionality."""

from unittest.mock import MagicMock, patch

import pytest

from svs_core.cli.tui.event_debouncer import EventDebouncer
from svs_core.cli.tui.state_manager import SelectionType, ThreadSafeStateManager


@pytest.mark.cli
class TestTUIStateManager:
    """Tests for TUI state management."""

    def test_set_selection_service(self) -> None:
        """Test setting service selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.SERVICE, 123)

        selection = manager.get_selection()
        assert selection.type == SelectionType.SERVICE
        assert selection.item_id == 123

    def test_set_selection_template(self) -> None:
        """Test setting template selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.TEMPLATE, 456)

        selection = manager.get_selection()
        assert selection.type == SelectionType.TEMPLATE
        assert selection.item_id == 456

    def test_set_selection_user(self) -> None:
        """Test setting user selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.USER, 789)

        selection = manager.get_selection()
        assert selection.type == SelectionType.USER
        assert selection.item_id == 789

    def test_clear_selection(self) -> None:
        """Test clearing selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.SERVICE, 123)
        manager.clear_selection()

        selection = manager.get_selection()
        assert selection.type == SelectionType.NONE
        assert selection.item_id is None

    def test_selection_overwrite(self) -> None:
        """Test that new selection overwrites old one."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.SERVICE, 123)
        manager.set_selection(SelectionType.TEMPLATE, 456)

        selection = manager.get_selection()
        assert selection.type == SelectionType.TEMPLATE
        assert selection.item_id == 456

    def test_operation_guard_basic(self) -> None:
        """Test basic operation guard."""
        manager = ThreadSafeStateManager()

        # First operation should succeed
        assert manager.start_operation() is True
        assert manager.is_operation_pending() is True

        # Second concurrent should fail
        assert manager.start_operation() is False

        # After end, should allow next
        manager.end_operation()
        assert manager.is_operation_pending() is False
        assert manager.start_operation() is True

    def test_operation_guard_after_end(self) -> None:
        """Test that operation guard releases properly."""
        manager = ThreadSafeStateManager()

        manager.start_operation()
        manager.end_operation()

        # Should be able to start new operation
        assert manager.start_operation() is True


@pytest.mark.cli
class TestTUIEventDebouncer:
    """Tests for TUI event debouncing."""

    def test_debounce_basic(self) -> None:
        """Test basic debounce functionality."""
        import time

        calls = []
        debouncer = EventDebouncer(delay_seconds=0.05)

        debouncer.debounce("test", lambda: calls.append(1))
        assert len(calls) == 0

        time.sleep(0.1)
        assert len(calls) == 1

    def test_debounce_cancellation(self) -> None:
        """Test that new debounce cancels previous."""
        import time

        calls = []
        debouncer = EventDebouncer(delay_seconds=0.05)

        debouncer.debounce("test", lambda: calls.append(1))
        time.sleep(0.02)
        debouncer.debounce("test", lambda: calls.append(2))

        time.sleep(0.1)
        # Only the second callback should execute
        assert len(calls) == 1
        assert calls[0] == 2

    def test_debounce_different_events(self) -> None:
        """Test debouncing multiple different events."""
        import time

        calls: dict[str, list[int]] = {"event1": [], "event2": []}
        debouncer = EventDebouncer(delay_seconds=0.05)

        debouncer.debounce("event1", lambda: calls["event1"].append(1))
        debouncer.debounce("event2", lambda: calls["event2"].append(2))

        time.sleep(0.1)
        assert len(calls["event1"]) == 1
        assert len(calls["event2"]) == 1

    def test_cancel_event(self) -> None:
        """Test cancelling a pending event."""
        import time

        calls = []
        debouncer = EventDebouncer(delay_seconds=0.05)

        debouncer.debounce("test", lambda: calls.append(1))
        debouncer.cancel("test")

        time.sleep(0.1)
        assert len(calls) == 0

    def test_cancel_all(self) -> None:
        """Test cancelling all pending events."""
        import time

        calls: dict[str, list[int]] = {"event1": [], "event2": []}
        debouncer = EventDebouncer(delay_seconds=0.05)

        debouncer.debounce("event1", lambda: calls["event1"].append(1))
        debouncer.debounce("event2", lambda: calls["event2"].append(2))
        debouncer.cancel_all()

        time.sleep(0.1)
        assert len(calls["event1"]) == 0
        assert len(calls["event2"]) == 0


@pytest.mark.cli
class TestTUIDataAccess:
    """Tests for TUI data access layer."""

    @pytest.mark.django_db
    def test_data_access_import(self) -> None:
        """Test that DataAccessLayer can be imported."""
        from svs_core.cli.tui.data_access import DataAccessLayer

        dal = DataAccessLayer()
        assert dal is not None
        assert dal._cache_ttl == 60.0

    @pytest.mark.django_db
    def test_data_access_service_not_found(self) -> None:
        """Test handling of non-existent service."""
        from svs_core.cli.tui.data_access import DataAccessLayer

        dal = DataAccessLayer()
        service = dal.get_service(999999)
        assert service is None

    @pytest.mark.django_db
    def test_data_access_template_not_found(self) -> None:
        """Test handling of non-existent template."""
        from svs_core.cli.tui.data_access import DataAccessLayer

        dal = DataAccessLayer()
        template = dal.get_template(999999)
        assert template is None

    @pytest.mark.django_db
    def test_data_access_user_not_found(self) -> None:
        """Test handling of non-existent user."""
        from svs_core.cli.tui.data_access import DataAccessLayer

        dal = DataAccessLayer()
        user = dal.get_user(999999)
        assert user is None

    @pytest.mark.django_db
    def test_data_access_cache_invalidation(self) -> None:
        """Test cache invalidation."""
        from svs_core.cli.tui.data_access import DataAccessLayer

        dal = DataAccessLayer()
        dal.invalidate_service_cache(123)
        dal.invalidate_template_cache(456)
        dal.invalidate_user_cache(789)
        dal.invalidate_all()

        # Should complete without errors


@pytest.mark.cli
class TestTUIModals:
    """Tests for TUI modal dialogs."""

    def test_create_service_modal_import(self) -> None:
        """Test that CreateServiceModal can be imported."""
        from svs_core.cli.tui.app import CreateServiceModal

        assert CreateServiceModal is not None

    def test_create_user_modal_import(self) -> None:
        """Test that CreateUserModal can be imported."""
        from svs_core.cli.tui.app import CreateUserModal

        assert CreateUserModal is not None

    def test_logs_modal_import(self) -> None:
        """Test that LogsModal can be imported."""
        from svs_core.cli.tui.app import LogsModal

        assert LogsModal is not None

    def test_import_template_modal_import(self) -> None:
        """Test that ImportTemplateModal can be imported."""
        from svs_core.cli.tui.app import ImportTemplateModal

        assert ImportTemplateModal is not None


@pytest.mark.cli
class TestTUIScreen:
    """Tests for TUI main screen."""

    def test_screen_import(self) -> None:
        """Test that SVSTUIScreen can be imported."""
        from svs_core.cli.tui.app import SVSTUIScreen

        assert SVSTUIScreen is not None

    def test_screen_initialization(self) -> None:
        """Test screen initialization."""
        from svs_core.cli.tui.app import SVSTUIScreen

        screen = SVSTUIScreen()
        assert screen.state_manager is not None
        assert screen.data_access is not None
        assert screen.event_debouncer is not None

    def test_screen_bindings(self) -> None:
        """Test screen key bindings."""
        from svs_core.cli.tui.app import SVSTUIScreen

        screen = SVSTUIScreen()
        assert len(screen.BINDINGS) == 2
        assert isinstance(screen.BINDINGS[0], tuple)
        assert isinstance(screen.BINDINGS[1], tuple)
        assert screen.BINDINGS[0][0] == "q"  # Quit
        assert screen.BINDINGS[1][0] == "r"  # Refresh


@pytest.mark.cli
class TestTUILoginScreen:
    """Tests for TUI login screen."""

    def test_login_screen_import(self) -> None:
        """Test that LoginScreen can be imported."""
        from svs_core.cli.tui.web import LoginScreen

        assert LoginScreen is not None

    def test_login_app_import(self) -> None:
        """Test that LoginApp can be imported."""
        from svs_core.cli.tui.web import LoginApp

        assert LoginApp is not None
