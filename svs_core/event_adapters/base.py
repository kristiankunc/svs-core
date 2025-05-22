from __future__ import annotations
from abc import ABCMeta, abstractmethod
from typing import (
    TYPE_CHECKING,
    cast,
    Callable,
    ClassVar,
    List,
    Any,
    ParamSpec,
    Concatenate,
)

if TYPE_CHECKING:
    from svs_core.users.user import User
    from svs_core.users.ssh_key import SSHKey

P = ParamSpec("P")


class SideEffectAdapterMeta(ABCMeta):
    """
    Metaclass for SideEffectAdapter that keeps track of all instances.
    Meaning if a class inherits from SideEffectAdapter, it will be registered
    in the SideEffectAdapterMeta class.

    This allows us to dispatch operations to all instances of SideEffectAdapter from static context.
    """

    _instances: ClassVar[List[SideEffectAdapter]] = []

    def __call__(cls, *args: Any, **kwargs: Any) -> SideEffectAdapter:
        instance = super().__call__(*args, **kwargs)
        cls._instances.append(instance)
        return cast(SideEffectAdapter, instance)

    @classmethod
    def get_all_instances(cls) -> List[SideEffectAdapter]:
        return SideEffectAdapterMeta._instances[:]


class SideEffectAdapter(metaclass=SideEffectAdapterMeta):
    """
    Abstract base class for side effect adapters.
    This class is used to define the interface for side effect adapters (those that do not return a value).

    Calling a dispatch method assumes that all conditions for the operation are met.
    (e.g. user with the same name does not exist already)
    """

    @abstractmethod
    def _create_user(self, username: str) -> None: ...

    @abstractmethod
    def _delete_user(self, user: User) -> None: ...

    @abstractmethod
    def _add_ssh_key(self, user: User, key_name: str, key_content: str) -> None: ...

    @abstractmethod
    def _delete_ssh_key(self, user: User, ssh_key: SSHKey) -> None: ...

    @classmethod
    def _dispatch(
        cls,
        operation: Callable[Concatenate[SideEffectAdapter, P], None],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> None:
        """
        Dispatches an operation to all instances of SideEffectAdapter.
        """
        for impl in SideEffectAdapterMeta.get_all_instances():
            operation(impl, *args, **kwargs)

    @classmethod
    def dispatch_create_user(cls, username: str) -> None:
        cls._dispatch(SideEffectAdapter._create_user, username)

    @classmethod
    def dispatch_delete_user(cls, user: User) -> None:
        cls._dispatch(SideEffectAdapter._delete_user, user)

    @classmethod
    def dispatch_add_ssh_key(cls, user: User, key_name: str, key_content: str) -> None:
        cls._dispatch(SideEffectAdapter._add_ssh_key, user, key_name, key_content)

    @classmethod
    def dispatch_delete_ssh_key(cls, user: User, ssh_key: SSHKey) -> None:
        cls._dispatch(SideEffectAdapter._delete_ssh_key, user, ssh_key)
