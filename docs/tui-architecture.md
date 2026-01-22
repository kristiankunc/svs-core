# SVS Core TUI Architecture

This document describes the architecture, design patterns, and implementation details of the SVS Core Terminal User Interface (TUI).

## Overview

The TUI is a Textual-based terminal application that provides a user-friendly interface for managing SVS Core services, templates, and users. It was redesigned to address critical reliability issues with the original implementation.

**Location**: `svs_core/cli/tui/app.py` and supporting modules

## Architecture Layers

### 1. State Management Layer (`state_manager.py`)

**Purpose**: Provide thread-safe state management for UI selections and operation guards.

**Key Components**:

- `SelectionType` enum: Defines types of selectable items (SERVICE, TEMPLATE, USER, NONE)
- `Selection` dataclass: Immutable representation of a selected item
- `ThreadSafeStateManager`: Main class managing all state with thread-safety

**Thread Safety Mechanism**:
- Uses `threading.RLock()` for recursive locking
- All state modifications protected by locks
- Atomic operations prevent race conditions

**Key Methods**:
```python
set_selection(type, item_id)      # Update current selection
get_selection() -> Selection       # Get current selection
start_operation() -> bool          # Guard concurrent operations
end_operation()                    # Release operation guard
```

**Why It Matters**:
- Prevents race conditions when multiple worker threads modify state
- Ensures only one operation (start/stop/delete) runs at a time
- Guards against UI state corruption

### 2. Data Access Layer (`data_access.py`)

**Purpose**: Provide intelligent caching and thread-safe database access.

**Key Components**:

- `CacheEntry`: Wrapper for cached data with TTL (time-to-live)
- `DataAccessLayer`: Main class handling all database operations

**Caching Strategy**:
- Default TTL: 60 seconds
- Separate caches for services, templates, and users
- Automatic expiration of stale entries
- Manual invalidation after operations

**Key Methods**:
```python
get_service(id) -> Service          # Get with caching
get_template(id) -> Template        # Get with caching
get_user(id) -> User                # Get with caching
get_all_services()                  # List with caching
invalidate_service_cache(id)        # Clear cache entry
invalidate_all()                    # Clear all caches
```

**Lazy Imports**:
All Django model imports are done inside methods (not at module level) to avoid circular imports and ensure Django is properly initialized before accessing models.

**Why It Matters**:
- Reduces database queries dramatically (50+ per scroll event → 0)
- Prevents redundant operations during scrolling
- Maintains data consistency with TTL-based expiration

### 3. Event Debouncing Layer (`event_debouncer.py`)

**Purpose**: Throttle rapid events to prevent cascading database queries.

**Key Components**:

- `EventDebouncer`: Main class managing delayed event execution

**Debouncing Strategy**:
- Default delay: 150ms
- Per-event-ID tracking with independent timers
- Cancels previous timer when new event arrives
- Daemon threads for cleanup

**Key Methods**:
```python
debounce(event_id, callback)        # Debounce an event
cancel(event_id)                    # Cancel specific event
cancel_all()                        # Cancel all pending events
```

**Usage Example**:
```python
# Debounce list selection to prevent rapid queries
self.event_debouncer.debounce(
    "service_detail",
    lambda: self.fetch_service_details(item_id)
)
```

**Why It Matters**:
- Prevents query cascades when user rapidly scrolls or clicks
- Responsive UI: still feels immediate with 150ms delay
- Reduces unnecessary database operations

## Main Application (`app.py`)

### Key Screens

**SVSTUIScreen**: Main application screen with three sections
- Services list (left panel)
- Templates list (left panel, below services)
- Users list (left panel, below templates)
- Details panel (right)
- Action buttons (right)

**Modal Screens**:
- `CreateServiceModal`: Form for creating new services
- `CreateUserModal`: Form for creating new users
- `ImportTemplateModal`: Form for importing templates
- `LogsModal`: Display service logs
- `ConfirmationModal`: Confirm destructive actions

### Operation Patterns

#### Safe Worker Operations

All operations that modify state run in worker threads:

```python
@work(thread=True)
def start_service(self, service_id: int) -> None:
    # 1. Check if operation is already pending
    if not self.state_manager.start_operation():
        self.app.call_from_thread(self.show_error, "Operation in progress")
        return
    
    try:
        # 2. Get data (cached)
        service = self.data_access.get_service(service_id)
        
        # 3. Perform operation
        service.start()
        
        # 4. Invalidate cache
        self.data_access.invalidate_service_cache(service_id)
        
        # 5. Update UI (thread-safe)
        self.app.call_from_thread(self.show_success, "Service started")
        self.app.call_from_thread(self.action_refresh)
    except Exception as e:
        self.app.call_from_thread(self.show_error, str(e))
    finally:
        self.state_manager.end_operation()  # Always release guard
```

**Key Characteristics**:
1. **Operation Guard**: Prevents concurrent operations
2. **Exception Handling**: All exceptions caught and displayed
3. **UI Updates**: All UI calls wrapped with `call_from_thread()`
4. **Cache Invalidation**: Stale data cleared after operations
5. **Cleanup**: Operation guard always released in finally block

#### Safe UI Queries in Workers

Worker threads can safely query UI elements:

```python
@work(thread=True)
def some_worker(self):
    try:
        # Try to get widget
        widget = self.query_one("#id", Button)
        # UI may have changed, handle gracefully
    except Exception:
        return  # Abort if UI changed
```

#### Debounced Event Handlers

List selection is debounced to prevent cascading queries:

```python
def on_list_view_selected(self, message: ListView.Selected) -> None:
    item_id = int(message.item.data)
    
    # Debounce to prevent rapid cascading queries
    self.event_debouncer.debounce(
        "service_detail",
        lambda: self.fetch_service_details(item_id)
    )
```

**Note**: `on_list_view_highlighted()` (scroll events) is intentionally empty to prevent queries during scrolling.

### Destructive Actions with Confirmation

All destructive actions now show confirmation dialogs:

**Delete Service**:
```python
def delete_service(self, service_id: int) -> None:
    try:
        service = self.data_access.get_service(service_id)
        if service:
            self.app.push_screen(
                ConfirmationModal(
                    "Delete Service",
                    f"Are you sure you want to delete '{service.name}'?"
                ),
                lambda confirmed: self._perform_delete_service(service_id) if confirmed else None
            )
    except Exception as e:
        self.show_error(f"Error: {e}")
```

The confirmation dialog is a modal screen that returns `True` if confirmed or `False` if cancelled. This pattern is used for:
- Delete Service
- Delete Template
- Delete User
- Reset User Password

## Design Decisions

### Why These Patterns?

1. **ThreadSafeStateManager**
   - Prevents race conditions in multi-threaded TUI
   - Simple, effective, easier to debug than complex synchronization
   - RLock allows same thread to re-acquire lock

2. **DataAccessLayer with Caching**
   - Original TUI triggered 50+ queries per scroll (MAJOR BUG)
   - Caching with TTL provides good balance: responsive UI + data freshness
   - 60s TTL means: if data changes externally, users see update within 60s
   - Manual invalidation ensures immediate consistency after operations

3. **EventDebouncer (150ms delay)**
   - Completely eliminates cascading query problem from rapid scrolling
   - 150ms is imperceptible to users (feels instant)
   - Balances responsiveness with preventing query storms

4. **Confirmation Dialogs**
   - Prevent accidental data loss
   - UX best practice for destructive operations
   - Users see exactly what they're deleting before confirming

5. **Worker Threads for All Operations**
   - Non-blocking UI: stays responsive during long operations
   - Prevents "frozen" UI while waiting for service start/stop
   - Exception handling ensures errors are displayed, not lost

## Performance Characteristics

### Scrolling Behavior

**Before Refactoring**:
- 50+ database queries per scroll event
- UI frequently froze during scroll
- Memory usage increased with each scroll

**After Refactoring**:
- 0 database queries during scrolling
- Smooth, responsive scrolling
- Memory stable during scrolling

### Operation Behavior

**Service Start/Stop/Delete**:
- Non-blocking: UI remains responsive
- Operation guard prevents concurrent operations
- Success/error notification displayed to user
- Cache invalidation ensures next refresh gets fresh data

### Data Freshness

- Data fetched on initial load
- Data refetched on user selection (debounced 150ms)
- Data refetched after operations (cache invalidated)
- Data refreshes automatically after 60s (TTL expiration)

## Testing Strategy

See `tests/cli/test_tui.py` and `tests/unit/test_tui_architecture.py` for test implementations.

**Key Test Areas**:
- State manager thread safety
- Event debouncer functionality
- Cache TTL and expiration
- Modal screen behavior
- Operation guards and error handling

## Future Improvements

1. **Real-time Refresh**: Implement service status refresh every 5 seconds
2. **Search/Filter**: Add ability to filter services by name or status
3. **Bulk Operations**: Start/stop multiple services at once
4. **Status Indicators**: Show uptime, resource usage in UI
5. **Persistent Cache TTL**: Make cache TTL configurable per UI
6. **Undo/Redo**: Implement undo for accidental deletions

## Debugging Guide

### Enable Debug Logging

Add to `SVSTUIScreen.__init__()`:
```python
import logging
logging.basicConfig(level=logging.DEBUG, filename="/tmp/tui_debug.log")
```

### Common Issues

1. **"Operation already in progress" message**
   - Caused by: Operation guard preventing concurrent operations
   - Solution: This is intentional - wait for operation to complete

2. **Stale data displayed**
   - Caused by: Cache TTL not expired yet
   - Solution: Click refresh button or wait up to 60 seconds

3. **UI freeze during service operation**
   - Should NOT happen with current implementation
   - If it does: Worker thread likely has exception - check logs

4. **Rapid clicking causing duplicate operations**
   - Prevented by: Operation guard + confirmation dialogs
   - Result: Safe - only one operation runs at a time

## Code References

**State Management**: `svs_core/cli/tui/state_manager.py`
**Data Access**: `svs_core/cli/tui/data_access.py`
**Event Debouncing**: `svs_core/cli/tui/event_debouncer.py`
**Main Application**: `svs_core/cli/tui/app.py`
**CSS Styling**: `svs_core/cli/tui/tui.css`
**Tests**: `tests/cli/test_tui.py`, `tests/unit/test_tui_architecture.py`

## Running the TUI

```bash
# Start the terminal UI
svs

# Start the web UI
python svs_core/cli/tui/server-runner.py
```

Both UIs share the same underlying logic and improvements.
