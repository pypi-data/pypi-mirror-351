from fakeredis import FakeRedis
from redis import Redis
import os
from dotenv import load_dotenv

from cache.data_sources.repository.cache_service_impl import CacheServiceImpl
from cache.domain.repository.cache_service import CacheService

load_dotenv()  # only needed if you haven't loaded env elsewhere


class CacheServiceFactory:
    @staticmethod
    def create(namespace: str = "cache_service") -> CacheService:
        redis_client = Redis(
            host=os.getenv("REDIS_HOST"),
            port=int(os.getenv("REDIS_PORT")),
            db=int(os.getenv("REDIS_DB")),
            decode_responses=False
        )
        return CacheServiceImpl(cache=redis_client, namespace=namespace)

    @staticmethod
    def createTest(disabled: bool = False) -> CacheService:
        redis_client = FakeRedis()
        return CacheServiceImpl(cache=redis_client, namespace="test", disabled=disabled)
