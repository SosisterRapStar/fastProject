from curses.ascii import US
import uuid
from requests import session
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary
from src.models.friends_model import Invite
from src.models.user_model import User
from .exceptions import RecordNotFoundError, AlreadyFriendException, NoFriendsException


class UserRepository(CRUDAlchemyRepository):
    _model = User

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_convs(self, user_id: uuid.UUID) -> list["Conversation"]:
        stmt = (
            select(Conversation)
            .join(
                UserConversationSecondary,
                Conversation.id == UserConversationSecondary.conversation_id,
            )
            .where(UserConversationSecondary.user_id == user_id)
        )
        res = await self._session.scalars(stmt)
        return list(res.all())

    async def get_user_messages(self, user_id: uuid.UUID):
        user = await self.get_user_with_messages(user_id)
        return user.messages

    async def get_user_with_messages(self, user_id: uuid.UUID) -> User:
        stmt = select(User).where(User.id == user_id).options(joinedload(User.messages))
        user = await self._session.scalar(stmt)
        return user
    
    
    
    # on each request we take all user friends very expensive
    async def add_friend(self, user: User, **criteries) -> User:
        
        try:
            friend = await self.get(**criteries)
        except RecordNotFoundError:
            raise RecordNotFoundError
        
        if await self.is_in_friend(user=user, friend=friend):
            raise RecordNotFoundError # for exampel of exception it will be refactored
        
        
        user.friends.add(friend)
       
        friend_friends = await friend.awaitable_attrs.friends
        friend_friends.add(user)
        await self._session.commit()
        
        return friend
        
    async def remove_friend(self, user: User, **criteries) -> User:
       
        try:
            friend = await self.get(**criteries)
        except RecordNotFoundError:
            raise RecordNotFoundError

        if not await self.is_in_friend(user=user, friend=friend):
            raise RecordNotFoundError # for exampel of exception it will be refactored
        
    
        user.friends.remove(friend)
        friend_friends = await friend.awaitable_attrs.friends
        friend_friends.remove(user)
        await self._session.commit()
        
        return friend
        
        

    async def is_in_friend(self, user: User, friend: User) -> User:
        return friend in await user.awaitable_attrs.friends
    
        
    async def get_all_friends(self, user: User) -> list[User]:
        user_friends = await user.awaitable_attrs.friends
        return list(user_friends)
    
    async def get_received_invites(self, user: User) -> list[Invite]:
        stmt = (
                select(Invite)
                .join(User, Invite.inviter_id == User.id)
                .where(Invite.invitee_id == user.id)
                .options(contains_eager(Invite.inviter))
            )
       
        return await self._session.scalars(stmt)
    
    async def get_sended_invites(self, user: User) -> list[Invite]:
        stmt = (
                select(Invite)
                .join(User, Invite.invitee_id == User.id)
                .where(Invite.inviter_id == user.id)
                .options(contains_eager(Invite.invitee))
            )
        return await self._session.scalars(stmt)