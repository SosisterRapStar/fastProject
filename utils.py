
import asyncio
# Ensure the src directory is in the PYTHONPATH
from sqlalchemy.utils.

from src.models.user_model import User
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncAttrs,
)
from src.models.chat_models import Conversation
from src.services.redis_service import RedisManager
from schemas.shcemas_from_db import ConversationFromDb
from sqlalchemy import select
from sqlalchemy.orm.base import instance_dict
import json 
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase

async def main():
    print(User.__name__)
    redis = RedisManager.get_connection()
    
    engine = create_async_engine("postgresql+asyncpg://vanya:1234@localhost:5433/test_fast_db")
    Session = async_sessionmaker(bind=engine)
    a = " "
    async with Session() as ses:  
            stmt = (
                select(Conversation)
                .where(Conversation.name=="fuck")
            )
            ans = await ses.scalar(stmt)
            
            await ans.awaitable_attrs.messages
            print(instance_dict(ans))
            try:
                ConversationFromDb.model_validate(ans.__dict__).model_dump_json()
            except: 
            # # await redis.hset("hz", mapping=a)
            
    
    
    
            
    

if __name__ == "__main__":
    asyncio.run(main())
# ttl_dict = dict()

# def g(key: str):
#     global ttl_dict
#     namespaces = key.split(":")[:-1]
    
#     curr_namespace = ttl_dict

#     for i in namespaces:
#         if i not in curr_namespace:
#             curr_namespace[i] = dict()
#         curr_namespace = curr_namespace[i]
#     curr_namespace["ttl"] = 10
#     print(ttl_dict)
    
# g("user:message:343334")
# g("user:list:232233")
# g("user:33223")
