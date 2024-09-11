from dataclasses import dataclass, field
from abc import ABC, abstractmethod


@dataclass
class AbstractCache(ABC):
    @abstractmethod
    async def get_key(self, key: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def set_key(self, key: str, value: str) -> None:
        raise NotImplementedError


# here will be memcached
@dataclass
class FakeCache(AbstractCache):
    cache: dict = field(default_factory=dict)

    @abstractmethod
    async def get_key(self, key: str) -> str:
        return self.cache.get(key)

    @abstractmethod
    async def set_key(self, key: str, value: str) -> None:
        self.cache[key] = value
