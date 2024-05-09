import redis.asyncio as redis
import asyncio 
from config import settings


class RedisManager:
    pool = redis.ConnectionPool(host=settings.redis.host, port=settings.redis.port, db=settings.redis.db, max_connections=settings.redis.max_pool_size)
    
    @classmethod
    def get_connection(cls):
        return redis.Redis(connection_pool=cls.pool, decode_responses=True)