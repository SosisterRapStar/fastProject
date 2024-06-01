import redis.asyncio as redis
import asyncio
from redis import Redis
from config import settings
from typing import Any, Dict, List
from src.config import settings
from abc import ABC, abstractmethod

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



class AbstractCache(ABC):
    
    @abstractmethod
    def set_ttl_for_namespace(self, key: str, ttl: int):
        raise NotImplementedError
    
    @abstractmethod
    def get_ttl_for_namespace(self, key: str):
        raise NotImplementedError
    
    @abstractmethod
    async def get_value(self, key: str):
        raise NotImplementedError
    
    @abstractmethod
    async def set_value(self, key: str, value: Any):
        raise NotImplementedError
    
    @abstractmethod
    async def set_object(self, key: str, object: Dict[str, Any]):
        raise NotImplementedError
    
    @abstractmethod
    async def get_object(self, key: str) -> Dict[str, Any]:
        raise NotImplementedError
    
    @abstractmethod
    async def set_list(self, key: str, value: List[Any]):
        raise NotImplementedError
    
    @abstractmethod
    async def get_list(self, key: str):
        raise NotImplementedError
    
    @abstractmethod
    async def delete_key(self, key: str) -> str:
        raise NotImplementedError
    
    @abstractmethod
    async def add_to_list(self, key: str, value: Any):
        raise NotImplementedError
    
    @abstractmethod
    async def remove_from_the_list(self, key: str, value: Any):
        raise NotImplemented

class RedisCache(AbstractCache):
    # stores ttls for namespaces in cache like: {user: {ttl (ttl of user namespace): 10s, messages: {ttl: 15s ...}}}
    _ttl_for_namespaces = {} # helps to regulate ttl for different purposes
    
    '''
    Structure of namespace should implement the following format 
    main_namespace:sub_namespace1:...:id (id of entity in the main namespace)
    '''
    
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
        
        
    async def get_string(self, key: str) -> Any | None:
        async with self.redis() as r:
            return await r.get(key)
    
        
    async def set_string(self, key: str, value: str) -> Dict[str, str]:
        async with self.redis() as r:
            await r.set(key, value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
            return {key: value}
    
    async def set_object(self, key: str, object: Dict[str, Any]) -> None:
        async with self.redis() as r:
            await r.hset(key, mapping=object)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
    async def get_object(self, key: str) -> Dict[str, Any] | None:
        async with self.redis() as r:
            value = await r.hgetall(key)
            if value is not None:
                return value
            return None # BAN
            
        
    async def set_list(self, key: str, value:  List[Any]) -> None:
        async with self.redis() as r:
            await redis.rpush(key, *value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
    async def get_list(self, key: str) -> List[Any] | None:
        async with self.redis() as r:
            res = await r.lrange(key, 0, -1)
            if res is not None:
                return res
            return None # WARNING
        
    async def delete_key(self, key: str) -> str:
        async with self.redis() as r:
             await r.delete(key)
        return key
    
    
    async def add_to_list(self, key: str, value: Any):
        async with self.redis() as r:
            await r.rpush(key, value)
            
    async def remove_from_the_list(self, key: str, value: Any):
        return await super().remove_from_the_list(key, value)
        