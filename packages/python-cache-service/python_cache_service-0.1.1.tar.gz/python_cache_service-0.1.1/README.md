# python-cache-service

**A lightweight, namespaced caching service using Redis.**  
Supports fast prototyping and production-ready use, with built-in support for Redis and `fakeredis` for tests.

---

## 🚀 Features

- 🔑 Namespaced keys to avoid collisions
- ⏳ Optional TTL for cache expiration
- 🧪 `fakeredis` support for seamless unit testing
- 🧩 Decorator to cache function results transparently
- 🧼 Cache clearing by namespace

---

## 📦 Installation

```bash
pip install python-cache-service
```
---
## Usage
```python

from cache.domain.factories.cache_service_factory import CacheServiceFactory

cache = CacheServiceFactory.create(namespace="my_app")

# Store a value
cache.set("my_key", {"data": 123}, ttl_seconds=3600)

# Retrieve a value
value = cache.get("my_key")

# Delete a value
cache.delete("my_key")

# Clear all keys in the namespace
cache.clear()
```

## Configuration

#### You can configure the cache service by setting environment variables:

- REDIS_HOST=localhost
- REDIS_PORT=6379
- REDIS_DB=0

## 🧪 Using in tests

```python
from cache.domain.factories.cache_service_factory import CacheServiceFactory

cache = CacheServiceFactory.createTest()

cache.set("test_key", [1, 2, 3])
assert cache.get("test_key") == [1, 2, 3]
```

#### You can also disable caching entirely in test mode:

```python
from cache.domain.factories.cache_service_factory import CacheServiceFactory
cache = CacheServiceFactory.createTest(disabled=True)
```

## 🎯 Using the @cache_result decorator

```python
from cache.decorators.cache_result import cache_result
from cache.domain.factories.cache_service_factory import CacheServiceFactory

cache = CacheServiceFactory.create(namespace="my_app")

@cache_result(cache, ttl_seconds=120, key_prefix="my_func", verbose=True)
def heavy_computation(x, y):
    return x + y

# First call: computed and cached
heavy_computation(2, 3)

# Second call: cache hit
heavy_computation(2, 3)
```

## 🧾 License
This project is licensed under the MIT License - see the LICENSE file for details.