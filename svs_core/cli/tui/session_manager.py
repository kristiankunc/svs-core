"""In-memory session management for SVS web and TUI interfaces.

This module provides thread-safe session management without database access.
Sessions are stored in memory with automatic expiration.
"""

import secrets
import threading
from datetime import datetime, timedelta
from typing import Any, Optional


class Session:
    """Represents a single user session."""

    def __init__(self, session_id: str, user_id: int, username: str, is_admin: bool, expires_at: datetime) -> None:
        """Initialize a session.

        Args:
            session_id: Unique session identifier
            user_id: ID of the user in this session
            username: Username of the user
            is_admin: Whether the user is an admin
            expires_at: When this session expires
        """
        self.session_id = session_id
        self.user_id = user_id
        self.username = username
        self.is_admin = is_admin
        self.expires_at = expires_at
        self.created_at = datetime.now()

    def is_expired(self) -> bool:
        """Check if this session has expired."""
        return datetime.now() > self.expires_at

    def extend(self, duration_hours: int = 24) -> None:
        """Extend the session expiration time.

        Args:
            duration_hours: Hours to extend the session for (default 24 hours)
        """
        self.expires_at = datetime.now() + timedelta(hours=duration_hours)


class SessionManager:
    """Thread-safe in-memory session manager."""

    def __init__(self, session_duration_hours: int = 24) -> None:
        """Initialize the session manager.

        Args:
            session_duration_hours: How long sessions last before expiration (default 24 hours)
        """
        self._sessions: dict[str, Session] = {}
        self._lock = threading.RLock()
        self._session_duration_hours = session_duration_hours
        self._cleanup_interval = 300  # Clean up expired sessions every 5 minutes

    def create_session(self, user_id: int, username: str, is_admin: bool) -> str:
        """Create a new session for a user.

        Args:
            user_id: ID of the user
            username: Username of the user
            is_admin: Whether the user is an admin

        Returns:
            The new session ID
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=self._session_duration_hours)

        with self._lock:
            self._sessions[session_id] = Session(
                session_id=session_id,
                user_id=user_id,
                username=username,
                is_admin=is_admin,
                expires_at=expires_at,
            )
            # Clean up expired sessions periodically
            self._cleanup_expired_sessions()

        return session_id

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID.

        Args:
            session_id: The session ID to retrieve

        Returns:
            The session if found and valid, None otherwise
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                return None

            if session.is_expired():
                del self._sessions[session_id]
                return None

            # Extend session on access (sliding window)
            session.extend(self._session_duration_hours)
            return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: The session ID to delete

        Returns:
            True if session was deleted, False if not found
        """
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False

    def _cleanup_expired_sessions(self) -> None:
        """Remove all expired sessions."""
        expired_ids = [
            sid for sid, session in self._sessions.items()
            if session.is_expired()
        ]
        for sid in expired_ids:
            del self._sessions[sid]

    def cleanup_expired_sessions(self) -> None:
        """Manually trigger cleanup of expired sessions."""
        with self._lock:
            self._cleanup_expired_sessions()

    def session_count(self) -> int:
        """Get the number of active sessions.

        Returns:
            Number of sessions currently in memory
        """
        with self._lock:
            return len(self._sessions)


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create the global session manager instance.

    Returns:
        The global SessionManager instance
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
