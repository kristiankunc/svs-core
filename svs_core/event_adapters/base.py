from abc import ABC, ABCMeta, abstractmethod
from enum import Enum
from typing import cast

class Event(Enum):
    CREATE_USER = "create_user"
    DELETE_USER = "delete_user"
    ADD_SSH_KEY = "add_ssh_key"
    DELETE_SSH_KEY = "delete_ssh_key"


class Dispatcher:
    _adapters: list["Adapter"] = []

    @classmethod
    def register(cls, adapter: "Adapter") -> None:
        cls._adapters.append(adapter)

    @classmethod
    def dispatch(cls, event: Event, *args: object, **kwargs: object) -> None:
        for adapter in cls._adapters:
            method = getattr(adapter, event.value, None)
            if callable(method):
                method(*args, **kwargs)



class AdapterMeta(ABCMeta):
    def __call__(cls, *args: object, **kwargs: object) -> "Adapter":
        instance = super().__call__(*args, **kwargs)
        Dispatcher.register(cast("Adapter", instance))
        return cast("Adapter", instance)


class Adapter(ABC, metaclass=AdapterMeta):
    @abstractmethod
    def create_user(self, username: str) -> None: pass

    @abstractmethod
    def delete_user(self, username: str) -> None: pass

    @abstractmethod
    def add_ssh_key(self, username: str, ssh_key: str) -> None: pass

    @abstractmethod
    def delete_ssh_key(self, username: str, ssh_key: str) -> None: pass
