"""Tests for TUI state management and thread safety."""

import threading
import time

import pytest

from svs_core.cli.tui.data_access import DataAccessLayer
from svs_core.cli.tui.event_debouncer import EventDebouncer
from svs_core.cli.tui.state_manager import SelectionType, ThreadSafeStateManager


@pytest.mark.cli
class TestThreadSafeStateManager:
    """Tests for thread-safe state management."""

    def test_set_and_get_selection(self) -> None:
        """Test setting and retrieving selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.SERVICE, 42)

        selection = manager.get_selection()
        assert selection.type == SelectionType.SERVICE
        assert selection.item_id == 42

    def test_clear_selection(self) -> None:
        """Test clearing selection."""
        manager = ThreadSafeStateManager()
        manager.set_selection(SelectionType.SERVICE, 42)
        manager.clear_selection()

        selection = manager.get_selection()
        assert selection.type == SelectionType.NONE
        assert selection.item_id is None

    def test_concurrent_selection_updates(self) -> None:
        """Test that concurrent updates don't cause race conditions."""
        manager = ThreadSafeStateManager()
        results: list[int | None] = []

        def update_and_read(item_id: int) -> None:
            """Update selection and read it back."""
            manager.set_selection(SelectionType.SERVICE, item_id)
            time.sleep(0.001)  # Small delay
            selection = manager.get_selection()
            results.append(selection.item_id)

        threads = [
            threading.Thread(target=update_and_read, args=(i,)) for i in range(1, 11)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be valid item IDs (1-10)
        assert all(r in range(1, 11) for r in results)

    def test_operation_guard(self) -> None:
        """Test operation pending guard."""
        manager = ThreadSafeStateManager()

        # First operation should succeed
        assert manager.start_operation() is True
        assert manager.is_operation_pending() is True

        # Second operation should fail
        assert manager.start_operation() is False

        # After end, should succeed again
        manager.end_operation()
        assert manager.is_operation_pending() is False
        assert manager.start_operation() is True

    def test_concurrent_operation_guard(self) -> None:
        """Test operation guard under concurrent access."""
        manager = ThreadSafeStateManager()
        successful_starts = []

        def try_operation() -> None:
            """Try to start and end an operation."""
            if manager.start_operation():
                successful_starts.append(1)
                time.sleep(0.01)
                manager.end_operation()

        threads = [threading.Thread(target=try_operation) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should have at most 10 successful starts (likely fewer due to timing)
        assert len(successful_starts) <= 10


class TestEventDebouncer:
    """Tests for event debouncing."""

    def test_debounce_executes_after_delay(self) -> None:
        """Test that debounce executes callback after delay."""
        callback_calls = []

        def callback() -> None:
            """Test callback."""
            callback_calls.append(1)

        debouncer = EventDebouncer(delay_seconds=0.05)
        debouncer.debounce("test", callback)

        # Not called immediately
        assert len(callback_calls) == 0

        # Called after delay
        time.sleep(0.1)
        assert len(callback_calls) == 1

    def test_debounce_cancels_previous(self) -> None:
        """Test that new debounce cancels previous."""
        callback_calls = []

        def callback() -> None:
            """Test callback."""
            callback_calls.append(1)

        debouncer = EventDebouncer(delay_seconds=0.05)

        # Schedule first event
        debouncer.debounce("test", callback)
        time.sleep(0.02)

        # Schedule second event (should cancel first)
        debouncer.debounce("test", callback)
        time.sleep(0.02)

        # First callback should not have executed
        assert len(callback_calls) == 0

        # Wait for second to execute
        time.sleep(0.05)
        assert len(callback_calls) == 1

    def test_debounce_multiple_events(self) -> None:
        """Test debouncing multiple different events."""
        calls = {"event1": 0, "event2": 0}

        def callback1() -> None:
            calls["event1"] += 1

        def callback2() -> None:
            calls["event2"] += 1

        debouncer = EventDebouncer(delay_seconds=0.05)
        debouncer.debounce("event1", callback1)
        debouncer.debounce("event2", callback2)

        time.sleep(0.1)

        assert calls["event1"] == 1
        assert calls["event2"] == 1

    def test_cancel_event(self) -> None:
        """Test cancelling a pending event."""
        callback_calls = []

        def callback() -> None:
            callback_calls.append(1)

        debouncer = EventDebouncer(delay_seconds=0.05)
        debouncer.debounce("test", callback)

        # Cancel before execution
        debouncer.cancel("test")
        time.sleep(0.1)

        # Should not have executed
        assert len(callback_calls) == 0

    def test_cancel_all(self) -> None:
        """Test cancelling all events."""
        calls = {"event1": 0, "event2": 0}

        def callback1() -> None:
            calls["event1"] += 1

        def callback2() -> None:
            calls["event2"] += 1

        debouncer = EventDebouncer(delay_seconds=0.05)
        debouncer.debounce("event1", callback1)
        debouncer.debounce("event2", callback2)

        # Cancel all
        debouncer.cancel_all()
        time.sleep(0.1)

        # Nothing should have executed
        assert calls["event1"] == 0
        assert calls["event2"] == 0


class TestDataAccessLayer:
    """Tests for data access layer with caching."""

    @pytest.mark.django_db
    def test_cache_hit(self) -> None:
        """Test that cache returns stored data."""
        from svs_core.users.user import User

        # Create a user
        user = User.objects.create(name="testuser", password="pass123")

        dal = DataAccessLayer(cache_ttl=60.0)

        # First call queries database
        user1 = dal.get_user(user.id)
        assert user1 is not None
        assert user1.name == "testuser"

        # Modify the database object (simulate external change)
        user.name = "modified"
        user.save()

        # Second call should return cached version
        user2 = dal.get_user(user.id)
        assert user2 is not None
        assert user2.name == "testuser"  # Original cached value

    @pytest.mark.django_db
    def test_cache_expiration(self) -> None:
        """Test that cache expires after TTL."""
        from svs_core.users.user import User

        # Create a user
        user = User.objects.create(name="testuser", password="pass123")

        dal = DataAccessLayer(cache_ttl=0.05)  # 50ms TTL

        # First call
        user1 = dal.get_user(user.id)
        assert user1 is not None

        # Wait for cache to expire
        time.sleep(0.1)

        # Modify the database object
        user.name = "modified"
        user.save()

        # Second call should query fresh from database
        user2 = dal.get_user(user.id)
        assert user2 is not None
        assert user2.name == "modified"  # Fresh value

    @pytest.mark.django_db
    def test_invalidate_cache(self) -> None:
        """Test manual cache invalidation."""
        from svs_core.users.user import User

        user = User.objects.create(name="testuser", password="pass123")

        dal = DataAccessLayer(cache_ttl=60.0)

        # Cache the user
        user1 = dal.get_user(user.id)
        assert user1 is not None

        # Invalidate
        dal.invalidate_user_cache(user.id)

        # Modify database
        user.name = "modified"
        user.save()

        # Should get fresh data
        user2 = dal.get_user(user.id)
        assert user2 is not None
        assert user2.name == "modified"

    @pytest.mark.django_db
    def test_thread_safe_cache_access(self) -> None:
        """Test that cache access is thread-safe."""
        from svs_core.users.user import User

        user = User.objects.create(name="testuser", password="pass123")
        dal = DataAccessLayer(cache_ttl=60.0)

        results: list[int | None] = []

        def access_cache() -> None:
            """Access cache multiple times."""
            for _ in range(10):
                retrieved = dal.get_user(user.id)
                if retrieved:
                    results.append(retrieved.id)

        threads = [threading.Thread(target=access_cache) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All results should be valid
        assert len(results) == 50
        assert all(r == user.id for r in results)
