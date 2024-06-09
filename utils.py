
import asyncio
# Ensure the src directory is in the PYTHONPATH


from src.models.user_model import User
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncAttrs,
)
from src.models.chat_models import Conversation
from sqlalchemy.orm.state import InstanceState
from src.services.redis_service import RedisManager
from schemas.shcemas_from_db import RawDBConversation, ConversationWithMessages
from sqlalchemy import select
from sqlalchemy.orm.base import instance_dict
import json 
from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from src.models.base import Base
from redis.commands.json.path import Path


from typing import Optional
from typing import Type


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
            # await ans.awaitable_attrs.messages
            schema = RawDBConversation.model_validate(ans).model_dump(mode='json')
            print(schema)
            
            
            # print(instance_dict(ans))
            # convert_to_pydantic_model(ConversationFromDb, sql_object=ans)
            # ConversationFromDb.model_validate(ans.__dict__).model_dump_json()
            
            # await redis.hset("hz", mapping=schema)
            async with redis as r:
                # await r.hset("ass", mapping=schema)
                val = await r.hgetall("ass")
                print(RawDBConversation.model_validate(val))
                
                # await r.json().set('hz', Path.root_path(), schema)
                # await r.expire("hz", 1000)
                await r.sadd("set", *[1, 1, 2, 3, 4, 5, 6, 7, 10])
                print(await r.smembers('set'))

            # redis.close()
            await redis.aclose()
            print(a)
            

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
