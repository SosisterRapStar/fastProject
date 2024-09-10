from services.broker_service import Broker
from src.services.redis_service import RedisManager
from typing import Annotated
from fastapi import Depends


async def get_broker() -> Broker:
    return Broker(publisher=RedisManager.get_connection(), subscriber=RedisManager.get_connection())


broker_provider = Annotated[Broker, 
                                  Depends(get_broker)]

