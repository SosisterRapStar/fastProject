import redis.asyncio as redis
import asyncio
from redis import Redis
from config import settings
from typing import Any, Dict, List, Optional, Union
from src.config import settings
from abc import ABC, abstractmethod
from pydantic import BaseModel
from redis.exceptions import DataError, RedisError
from .logger import log
from redis.commands.json.path import Path

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
        return redis.Redis.from_pool(connection_pool=cls.pool)
    # @classmethod
    # def close(cls) -> Redis:




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
    
    # @abstractmethod
    # async def set_set(self, key: str, value: Any):
    #     raise NotImplemented
    
    # @abstractmethod
    # async def get_set(self, key: str):
    #     raise NotImplemented
    
    @abstractmethod
    async def update_ttl(self, key: str):
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
        async with self.redis as r:
            return await r.get(key)
    
        
    async def set_string(self, key: str, value: str) -> Dict[str, str]:
        async with self.redis as r:
            await r.set(key, value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
            return {key: value}
    
    async def set_object(self, key: str, object: Union[Dict[str, Any], Any] | Any, schema: Optional[BaseModel] = None, as_json: bool=False, ) -> None:
        
        if not isinstance(object, dict):
            if schema is None:
                log.error("Schema must be provided for non-dict objects")
                raise ValueError("Schema must be provided for non-dict objects")
            object = schema.model_validate(object).model_dump(mode='json')

        async with self.redis as r:
            if as_json:
                await r.json().set(key, Path.root_path(), object)
               
            else:
                try:
                    await r.hset(key, mapping=object)
                except DataError:
                    log.error(f"Data can not be saved like hash: {DataError}")
                    raise DataError
                

            await r.expire(key, self.get_ttl_for_namespace(key=key))

                
    
    async def get_object(self, key: str, json: bool = False, schema: Optional[BaseModel] = None) -> Optional[Union[Any, Dict[str, Any]]]:
        async with self.redis as r:
            if json:
                value = await r.json().get(key, Path.root_path())
                
            else:
                value = await r.hgetall(key)

            if value is None:
                return None
            
            if schema:
                return schema.model_validate(value)
            
            return value
        
    async def set_sets(self, key: str, value: List[Any]) -> None:
        async with self.redis as r:
            await r.sadd(key, *value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))


    async def get_sets(self, key: str):
        async with self.redis as r:
            try:
                members = await r.smembers(key)
                return set(members)
            except RedisError as e:
                log.error(f"Error getting members of set {key}: {e}")
                raise
    async def is_in_set(self, key: str, value: Any):
        async with self.redis as r:
            try:
                return await r.sismember(key, value)
            except RedisError as e:
                log.error(f"Error checking membership in set {key}: {e}")
                raise
    
    async def add_to_set(self, key: str, value: Any):
        async with self.redis as r:
            await r.sadd(key, value)

    async def remove_from_set(self, key: str, value):
        async with self.redis as r:
            try:
                return await r.srem(key, value)
            except RedisError as e:
                log.error(f"Error removing from set {key}: {e}")
                raise

        
    async def set_list(self, key: str, value:  List[Any]) -> None:
        async with self.redis as r:
            await redis.rpush(key, *value)
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
    async def get_list(self, key: str) -> List[Any] | None:
        async with self.redis as r:
            res = await r.lrange(key, 0, -1)
            if res is not None:
                return res
            return None # WARNING
        
    async def delete_key(self, key: str) -> str:
        async with self.redis as r:
             await r.delete(key)
        return key

        
    

    
    
    async def add_to_list(self, key: str, value: Any):
        
        async with self.redis as r:
            if await self.get_list(key=key) is None:
                await r.expire(key, self.get_ttl_for_namespace(key=key))
            await r.rpush(key, value)
            
    async def remove_from_the_list(self, key: str, value: Any):
        return await super().remove_from_the_list(key, value)
    
    
    async def update_ttl(self, key):
        async with self.redis as r:
            await r.expire(key, self.get_ttl_for_namespace(key=key))
    
        