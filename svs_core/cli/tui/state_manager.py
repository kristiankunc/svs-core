"""Thread-safe state management for TUI."""

import threading
from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar

T = TypeVar("T")


class SelectionType(Enum):
    """Types of items that can be selected."""

    SERVICE = "service"
    TEMPLATE = "template"
    USER = "user"
    NONE = "none"


@dataclass
class Selection:
    """Represents a selected item with thread-safe access."""

    type: SelectionType
    item_id: int | None = None

    @staticmethod
    def none() -> "Selection":
        """Create a null selection."""
        return Selection(type=SelectionType.NONE)


class ThreadSafeStateManager:
    """Manages TUI state with thread safety using locks."""

    def __init__(self) -> None:
        """Initialize state manager."""
        self._lock = threading.RLock()
        self._selection = Selection.none()
        self._is_operation_pending = False

    def set_selection(self, selection_type: SelectionType, item_id: int) -> None:
        """Safely update selection."""
        with self._lock:
            self._selection = Selection(type=selection_type, item_id=item_id)

    def clear_selection(self) -> None:
        """Clear current selection."""
        with self._lock:
            self._selection = Selection.none()

    def get_selection(self) -> Selection:
        """Get current selection atomically."""
        with self._lock:
            return self._selection

    def start_operation(self) -> bool:
        """Mark operation as pending. Returns False if operation already pending."""
        with self._lock:
            if self._is_operation_pending:
                return False
            self._is_operation_pending = True
            return True

    def end_operation(self) -> None:
        """Mark operation as complete."""
        with self._lock:
            self._is_operation_pending = False

    def is_operation_pending(self) -> bool:
        """Check if operation is pending."""
        with self._lock:
            return self._is_operation_pending
