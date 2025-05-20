from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from typing import Callable, Protocol, TypeVar
from svs_core.users.user import User
from svs_core.users.ssh_key import SSHKey
from typing import cast

class Event(Enum):
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    ADD_SSH_KEY = "add_ssh_key"
    DELETE_SSH_KEY = "delete_ssh_key"


class SideEffectHandler(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> None: ...


class ResultHandler(Protocol):
    def __call__(self, *args: object, **kwargs: object) -> object: ...


F = TypeVar("F", bound=Callable[..., object])

def on_event(event: Event) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, "_is_event_handler", True)
        setattr(func, "_event", event)
        return func
    return decorator


class Adapter(ABC):
    pass


class AdapterMeta(ABCMeta):
    def __call__(cls, *args: object, **kwargs: object) -> Adapter:
        instance: Adapter = super().__call__(*args, **kwargs)

        for attr_name in dir(instance):
            method = getattr(instance, attr_name)

            if callable(method) and getattr(method, "_is_event_handler", False):
                event = getattr(method, "_event")

                if isinstance(instance, SideEffectAdapter):
                    Dispatcher.register(event, cast(SideEffectHandler, method))

                elif isinstance(instance, ResultAdapter):
                    Dispatcher.register_result(event, cast(ResultHandler, method))

        return instance

class SideEffectAdapter(Adapter, metaclass=AdapterMeta):
    def create_user(self, username: str) -> None: ...
    def delete_user(self, user: User) -> None: ...
    def add_ssh_key(self, user: User, key_name: str, key_content: str) -> None: ...
    def delete_ssh_key(self, user: User, ssh_key: SSHKey) -> None: ...

class ResultAdapter(Adapter, metaclass=AdapterMeta):
    @abstractmethod
    def create_user(self, username: str) -> User:
        pass

    @abstractmethod
    def delete_user(self, user: User) -> None:
        pass

    @abstractmethod
    def add_ssh_key(self, user: User, key_name: str, key_content: str) -> SSHKey:
        pass

    @abstractmethod
    def delete_ssh_key(self, user: User, ssh_key: SSHKey) -> None:
        pass


class Dispatcher:
    _side_effect_adapters: dict[Event, list[SideEffectHandler]] = {e: [] for e in Event}
    _result_adapters: dict[Event, ResultHandler] = {}

    @classmethod
    def register(cls, event: Event, method: SideEffectHandler) -> None:
        cls._side_effect_adapters[event].append(method)

    @classmethod
    def register_result(cls, event: Event, method: ResultHandler) -> None:
        if event in cls._result_adapters:
            raise RuntimeError(f"Result adapter for {event} already registered")
        cls._result_adapters[event] = method

    @classmethod
    def dispatch(cls, event: Event, *args: object, **kwargs: object) -> object:
        for method in cls._side_effect_adapters[event]:
            method(*args, **kwargs)

        result_method = cls._result_adapters.get(event)
        if result_method is None:
            raise RuntimeError(f"No result adapter registered for event {event}")

        return result_method(*args, **kwargs)
