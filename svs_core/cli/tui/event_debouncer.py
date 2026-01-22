"""Event debouncing for TUI to prevent rapid cascades."""

import threading
import time
from typing import Callable


class EventDebouncer:
    """Debounces rapid events to prevent cascade execution."""

    def __init__(self, delay_seconds: float = 0.1) -> None:
        """Initialize debouncer.

        Args:
            delay_seconds: Delay before executing the action after last event.
        """
        self._delay = delay_seconds
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def debounce(self, event_id: str, callback: Callable[[], None]) -> None:
        """Debounce an event.

        Args:
            event_id: Unique identifier for this event type.
            callback: Function to call after debounce delay.
        """
        with self._lock:
            # Cancel existing timer for this event
            if event_id in self._timers:
                self._timers[event_id].cancel()

            # Schedule new timer
            timer = threading.Timer(self._delay, lambda: self._execute(event_id, callback))
            timer.daemon = True
            timer.start()
            self._timers[event_id] = timer

    def _execute(self, event_id: str, callback: Callable[[], None]) -> None:
        """Execute the callback and clean up timer."""
        try:
            callback()
        finally:
            with self._lock:
                self._timers.pop(event_id, None)

    def cancel(self, event_id: str) -> None:
        """Cancel a pending debounced event."""
        with self._lock:
            if event_id in self._timers:
                self._timers[event_id].cancel()
                del self._timers[event_id]

    def cancel_all(self) -> None:
        """Cancel all pending debounced events."""
        with self._lock:
            for timer in self._timers.values():
                timer.cancel()
            self._timers.clear()
