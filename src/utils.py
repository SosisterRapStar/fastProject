import uuid
from typing import Union, Type

from fastapi import HTTPException
from sqlalchemy import select, Select, Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, selectinload

from src.models import db_handler
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.user_model import User
import asyncio


async def get_user(session: AsyncSession, user_name: str):
    user = await session.execute(select(User).where(User.name == user_name))
    return user.scalar()


async def create_conversation(session: AsyncSession):
    user = await get_user(session)
    new_conv = Conversation(name="New_conv", user_admin_fk=user.id)
    session.add(new_conv)
    await session.commit()
    return new_conv


async def get_scalar_result_or_404(session, stmt: Select):
    result = await session.scalar(stmt)
    if result is not None:
        return result
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def get_smthing_id_by_name(session: AsyncSession, name: str, smthing: Type[Type[DeclarativeBase]]):
    stmt = select(smthing.id).where(smthing.name == name)
    res = await get_scalar_result_or_404(session, stmt)
    return res


async def get_secondary(session: AsyncSession):
    return UserConversationSecondary()


async def add_user_to_conv(session: AsyncSession, user_name: str, conv_name: str):
    user_id = await get_smthing_id_by_name(session=session, name=user_name, smthing=User)
    conv_id = await get_smthing_id_by_name(session=session, name=conv_name, smthing=Conversation)
    sec = await get_secondary(session)
    sec.user_fk = user_id
    sec.conversation_fk = conv_id
    session.add(sec)
    await session.commit()



async def main():
    async with db_handler.session() as ses:
        # await add_user_to_conv(ses, user_name="I hate niggers2", conv_name="New_conv2")


        stmt = select(User).where(User.name == "I hate niggers2").options(selectinload(User.conversations))
        print(stmt.compile(db_handler.engine))
        # result: Result = await ses.execute(stmt)
        # user = result.scalar()
        # user = await ses.scalar(stmt)
        # print(user.conversations)
        # await ses.commit()

if __name__ == "__main__":
    asyncio.run(main())
