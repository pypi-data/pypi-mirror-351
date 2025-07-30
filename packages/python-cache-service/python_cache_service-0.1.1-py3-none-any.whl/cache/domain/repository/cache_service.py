from abc import ABC, abstractmethod
from typing import Optional, Any

from redis import Redis


class CacheService(ABC):

    def __init__(self, cache: Redis, namespace: str = "cache_service", disabled: bool = False):
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass
