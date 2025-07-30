import pickle
from typing import Optional, Any

from redis import Redis

from cache.domain.repository.cache_service import CacheService


class CacheServiceImpl(CacheService):


    def __init__(self, cache: Redis, namespace: str = "cache_service", disabled: bool = False):
        super().__init__(cache, namespace, disabled)
        self.cache = cache
        self.namespace = namespace
        self.disabled = disabled

    def _key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    def get(self, key: str) -> Optional[Any]:
        if self.disabled:
            return None
        raw = self.cache.get(self._key(key))
        if raw is None:
            return None
        return pickle.loads(raw)

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        if self.disabled:
            return
        raw = pickle.dumps(value)
        full_key = self._key(key)
        if ttl_seconds:
            self.cache.setex(full_key, ttl_seconds, raw)
        else:
            self.cache.set(full_key, raw)

    def delete(self, key: str) -> None:
        self.cache.delete(self._key(key))

    def clear(self) -> None:
        # Only clears keys in this namespace
        pattern = f"{self.namespace}:*"
        for k in self.cache.scan_iter(pattern):
            self.cache.delete(k)



