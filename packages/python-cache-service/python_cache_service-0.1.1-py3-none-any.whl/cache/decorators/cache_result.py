import functools
import hashlib
import json
from logging import getLogger

from cache.domain.repository.cache_service import CacheService


def cache_result(cache_service: CacheService, ttl_seconds: int = 3600, key_prefix: str = "", verbose: bool = False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Serialize the function args to create a unique cache key
            key_material = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
            key_hash = hashlib.sha256(key_material.encode()).hexdigest()
            cache_key = f"{key_prefix}:{func.__name__}:{key_hash}"

            try:
                cached = cache_service.get(cache_key)
                if cached not in (None, [], {}):
                    if verbose:
                        getLogger("@cache_result").info(f"Cache hit for {cache_key}")
                    return cached
                result = func(*args, **kwargs)
                cache_service.set(cache_key, result, ttl_seconds=ttl_seconds)
                if verbose:
                    getLogger("@cache_result").info(f"Cache miss for {cache_key}, setting cache")
                return result
            except Exception as e:
                if verbose:
                    getLogger("@cache_result").error(f"Cache error for {cache_key}: {e}")
                # In case of an error, we still want to execute the function
                # but we don't want to cache the result
                return func(*args, **kwargs)
        return wrapper
    return decorator