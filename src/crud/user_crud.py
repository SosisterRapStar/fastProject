import uuid

from sqlalchemy import select
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload

from src.models.user_model import User
from src.schemas.users import User_on_response, User_on_request, User_for_update





# async def load_user_with_convs(user_id: uuid.UUID,
#                                async_session: AsyncSession, ) -> User:
#     stmt = select(User).where(User.id == user_id).options(selectinload(User.conversations))
#     # user_with_convs = await get_user_or_404(stmt, session=session)
#     user = await async_session.scalar(stmt)
#     return user
