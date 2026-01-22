"""Data access layer for TUI with caching."""

import threading
import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CacheEntry:
    """A cached data entry with timestamp."""

    data: Any
    timestamp: float
    ttl_seconds: float = 60.0

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.timestamp > self.ttl_seconds

    def is_valid(self) -> bool:
        """Check if cache entry is valid."""
        return not self.is_expired()


class DataAccessLayer:
    """Thread-safe data access with caching to prevent redundant queries."""

    def __init__(self, cache_ttl: float = 60.0) -> None:
        """Initialize data access layer.

        Args:
            cache_ttl: Cache time-to-live in seconds.
        """
        self._lock = threading.RLock()
        self._cache_ttl = cache_ttl
        self._service_cache: dict[int, CacheEntry] = {}
        self._template_cache: dict[int, CacheEntry] = {}
        self._user_cache: dict[int, CacheEntry] = {}
        self._services_list_cache: CacheEntry | None = None
        self._templates_list_cache: CacheEntry | None = None
        self._users_list_cache: CacheEntry | None = None

    def _get_from_cache(self, cache_dict: dict[int, CacheEntry], item_id: int) -> Any | None:
        """Get item from cache if valid."""
        if item_id in cache_dict:
            entry = cache_dict[item_id]
            if entry.is_valid():
                return entry.data
            else:
                del cache_dict[item_id]
        return None

    def get_service(self, service_id: int) -> Any | None:
        """Get service by ID with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.docker.service import Service

        with self._lock:
            cached = self._get_from_cache(self._service_cache, service_id)
            if cached is not None:
                return cached

            try:
                service = Service.objects.get(id=service_id)
                self._service_cache[service_id] = CacheEntry(
                    data=service, timestamp=time.time(), ttl_seconds=self._cache_ttl
                )
                return service
            except Service.DoesNotExist:
                return None

    def get_template(self, template_id: int) -> Any | None:
        """Get template by ID with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.docker.template import Template

        with self._lock:
            cached = self._get_from_cache(self._template_cache, template_id)
            if cached is not None:
                return cached

            try:
                template = Template.objects.get(id=template_id)
                self._template_cache[template_id] = CacheEntry(
                    data=template, timestamp=time.time(), ttl_seconds=self._cache_ttl
                )
                return template
            except Template.DoesNotExist:
                return None

    def get_user(self, user_id: int) -> Any | None:
        """Get user by ID with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.users.user import User

        with self._lock:
            cached = self._get_from_cache(self._user_cache, user_id)
            if cached is not None:
                return cached

            try:
                user = User.objects.get(id=user_id)
                self._user_cache[user_id] = CacheEntry(
                    data=user, timestamp=time.time(), ttl_seconds=self._cache_ttl
                )
                return user
            except User.DoesNotExist:
                return None

    def get_all_services(self, filter_username: str | None = None) -> list[Any]:
        """Get all services with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.docker.service import Service

        with self._lock:
            if self._services_list_cache and self._services_list_cache.is_valid():
                return self._services_list_cache.data

            if filter_username:
                services = list(Service.objects.filter(user__name=filter_username))
            else:
                services = list(Service.objects.all())

            self._services_list_cache = CacheEntry(
                data=services, timestamp=time.time(), ttl_seconds=self._cache_ttl
            )
            return services

    def get_all_templates(self) -> list[Any]:
        """Get all templates with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.docker.template import Template

        with self._lock:
            if self._templates_list_cache and self._templates_list_cache.is_valid():
                return self._templates_list_cache.data

            templates = list(Template.objects.all())
            self._templates_list_cache = CacheEntry(
                data=templates, timestamp=time.time(), ttl_seconds=self._cache_ttl
            )
            return templates

    def get_all_users(self) -> list[Any]:
        """Get all users with caching."""
        # Import here to avoid circular imports and ensure Django is ready
        from svs_core.users.user import User

        with self._lock:
            if self._users_list_cache and self._users_list_cache.is_valid():
                return self._users_list_cache.data

            users = list(User.objects.all())
            self._users_list_cache = CacheEntry(
                data=users, timestamp=time.time(), ttl_seconds=self._cache_ttl
            )
            return users

    def invalidate_service_cache(self, service_id: int | None = None) -> None:
        """Invalidate service cache."""
        with self._lock:
            if service_id is not None:
                self._service_cache.pop(service_id, None)
            else:
                self._service_cache.clear()
            self._services_list_cache = None

    def invalidate_template_cache(self, template_id: int | None = None) -> None:
        """Invalidate template cache."""
        with self._lock:
            if template_id is not None:
                self._template_cache.pop(template_id, None)
            else:
                self._template_cache.clear()
            self._templates_list_cache = None

    def invalidate_user_cache(self, user_id: int | None = None) -> None:
        """Invalidate user cache."""
        with self._lock:
            if user_id is not None:
                self._user_cache.pop(user_id, None)
            else:
                self._user_cache.clear()
            self._users_list_cache = None

    def invalidate_all(self) -> None:
        """Invalidate all caches."""
        with self._lock:
            self._service_cache.clear()
            self._template_cache.clear()
            self._user_cache.clear()
            self._services_list_cache = None
            self._templates_list_cache = None
            self._users_list_cache = None

