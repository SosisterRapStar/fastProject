import redis.asyncio as redis
import asyncio
from redis import Redis
from config import settings
from typing import Any
from src.config import settings

class RedisManager:
    pool = redis.ConnectionPool(
        host=settings.redis.host,
        port=settings.redis.port,
        db=settings.redis.db,
        max_connections=settings.redis.max_pool_size,
        decode_responses=True,
    )

    @classmethod
    def get_connection(cls) -> Redis:
        return redis.Redis(connection_pool=cls.pool)




class RedisCache:
    # stores ttls for namespaces in cache like: {user: {ttl (ttl of user namespace): 10s, messages: {ttl: 15s ...}}}
    _ttl_for_namespaces = {}
    DEFAULT_TTL = settings.redis.DEFAULT_TTL
    
    def __init__(self, redis: Redis) -> None:
        self.redis = redis 
    
    def set_ttl_for_namespace(self, key: str, ttl: int) -> int:
        namespaces = key.split(":")[:-1]
        curr_namespace = self._ttl_for_namespaces
        
        for i in namespaces:
            if i not in curr_namespace:
                curr_namespace[i] = dict()
            curr_namespace = curr_namespace[i]
        curr_namespace["ttl"] = ttl
        return ttl
        
    def get_ttl_for_namespace(self, key: str) -> int:
        namespaces = key.split(":")[:-1]
        curr_namespace = self._ttl_for_namespaces
        for i in namespaces:
            if i not in curr_namespace:
                return self.DEFAULT_TTL
            curr_namespace = curr_namespace[i]
        return curr_namespace["ttl"] 
        
        
    async def get_key(self, key: str) -> any | None:
        async with self.redis() as r:
            return await r.get(key)
    
        
    async def set_key(self, key: str, value: str) -> dict[str, str]:
        async with self.redis() as r:
            await r.set(key, value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
            return {key: value}
    
    async def set_hset(self, key: str, value: dict) -> None:
        async with self.redis() as r:
            await r.hset(key, mapping=value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
    async def get_hset(self, key: str) -> dict[str, Any] | None:
        async with self.redis() as r:
            value = await r.hgetall(key)
            if value is not None:
                decoded_value = {k.decode('utf-8'): v.decode('utf-8') for k, v in value.items()}
                return decoded_value
            return None # WARN
            
        
    async def set_list(self, key: str, value: list) -> None:
        async with self.redis() as r:
            await redis.rpush(key, *value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
    async def get_list(self, key: str) -> list[Any] | None:
        async with self.redis() as r:
            res = await r.lrange(key, 0, -1)
            if res is not None:
                return [v.decode('utf-8') for v in res]
            return None # WARNING