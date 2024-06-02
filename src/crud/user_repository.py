from curses.ascii import US
import uuid
from requests import session
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload, contains_eager
from services.redis_service import AbstractCache
from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary, Message
from src.models.friends_model import Invite
from src.models.user_model import User
from .exceptions import RecordNotFoundError, AlreadyFriendException, NoFriendsException
from abc import abstractmethod
from repo_abstract import CRUDRepository, CacheCrudAlchemyRepository
from conversation_repository import ConversationRepository

from typing import List, TYPE_CHECKING


    


class AbstractUserRepository(CRUDRepository):
    @abstractmethod
    async def get_convs(self, user_id: uuid.UUID) -> list:
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_messages(self, user: User) -> list:
        raise NotImplementedError
    
    # @abstractmethod
    # async def get_user_with_messages(self):
    #     raise NotImplementedError
    
    @abstractmethod
    async def add_friend(self, user: User) -> "AbstractUserRepository":
        raise NotImplementedError
    
    @abstractmethod
    async def remove_friend(self, user: User) -> "AbstractUserRepository":
        raise NotImplementedError
    
    @abstractmethod
    async def remove_friend(self, user: User):
        raise NotImplementedError
    
    
    @abstractmethod
    async def  get_all_friends(self, user: User):
        raise NotImplementedError
    
    @abstractmethod
    async def  get_received_invites(self, user: User):
        raise NotImplementedError
    
    @abstractmethod
    async def  get_sended_invites(self, user: User):
        raise NotImplementedError
    

class UserRepository(CRUDAlchemyRepository, AbstractUserRepository):
    _model = User

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_convs(self, user_id: uuid.UUID) -> List["Conversation"]:
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

    async def get_user_messages(self, user_id: uuid.UUID) -> List["Message"]:
        user = await self.get_user_with_messages(user_id)
        return user.messages
    
    '''
    TODO: create service for messages in this service create logic for lazy loading 
    awaitable attrs using sqlalchemy functional like in services.friends_service
    '''
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
        
        

    async def is_in_friend(self, user: User, friend: User) -> bool:
        return friend in await user.awaitable_attrs.friends
    
        
    async def get_all_friends(self, user: User) -> List[User]:
        user_friends = await user.awaitable_attrs.friends
        return list(user_friends)
    
    async def get_received_invites(self, user: User) -> List[Invite]:
        stmt = (
                select(Invite)
                .join(User, Invite.inviter_id == User.id)
                .where(Invite.invitee_id == user.id)
                .options(contains_eager(Invite.inviter))
            )
       
        return await self._session.scalars(stmt)
    
    async def get_sended_invites(self, user: User) -> List[Invite]:
        stmt = (
                select(Invite)
                .join(User, Invite.invitee_id == User.id)
                .where(Invite.inviter_id == user.id)
                .options(contains_eager(Invite.invitee))
            )
        return await self._session.scalars(stmt)
    
    

class CacheUserRepository(CacheCrudAlchemyRepository, AbstractUserRepository):
    def __init__(self, repo: UserRepository, cache: AbstractCache, namespace_ttl: int) -> None:
        super().__init__(repo, cache, namespace_ttl)
        # will be refactored
        self.user_convs_namespace = f"{self.default_cache_namespace}:convs"
        self.user_sended_invites_namespace = f"{self.default_cache_namespace}:invites:sended"
        self.user_received_invites_namespace = f"{self.default_cache_namespace}:invites:received"
        self.user_friends_namespace = f"{self.default_cache_namespace}:friends"
        self.user_messages_namespace = f"{self.default_cache_namespace}:messages"
        
        self.cache.set_ttl_for_namespace(f"{self.user_convs_namespace}:id", ttl=500) # ttl is small because of duplicated info 
        self.cache.set_ttl_for_namespace(f"{self.user_sended_invites_namespace}:id", ttl=500)
        self.cache.set_ttl_for_namespace(f"{self.user_received_invites_namespace}:id", ttl=1000)
        self.cache.set_ttl_for_namespace(f"{self.user_friends_namespace}:id", ttl=1000)
        self.cache.set_ttl_for_namespace(f"{self.user_messages_namespace}:id", ttl=1000)
    
    async def get_convs(self, user_id: uuid.UUID):
        # this cache stores only cache keys of conversation objects
        
        if convs := await self.cache.get_list(key=f"{self.user_convs_namespace}:{user_id}") is not None:
            list = []
            for conv in convs:
                if cur_conv := await self.cache.get_object(key=f"{conv.__class.__name__}:{conv.id}") is not None:
                    list.append(await self.cache.get_object(key=f"{conv.__class.__name__}:{conv.id}"))
                    await self.cache.update_ttl(key=f"{conv.__class.__name__}:{conv.id}")
                else:
                    return await self.set_conv_user_cache(user_id=user_id)
            return list
        
        return await self.set_conv_user_cache(user_id=user_id)
        
        
    async def set_conv_user_cache(self, user_id):
        list_convs = await self.repo.get_convs(user_id=user_id)
        for conv in list_convs:
            if await self.cache.get_object(key=f"{conv.__class.__name__}:{conv.id}") is None:
                await self.cache.set_object(key=f"{conv.__class.__name__}:{conv.id}", object=conv.__dict__)
            else:
                await self.cache.update_ttl(key=f"{conv.__class.__name__}:{conv.id}")

            await self.cache.add_to_list(key=f"{self.user_convs_namespace}:{user_id}", value=f"{conv.__class.__name__}:{conv.id}")
            
        return list_convs
        
    async def set_messages_user_cache(self, user_id):
        list_messages = await self.repo.get_user_messages(user_id=user_id)

        for message in list_messages:
            if await self.cache.get_object(key=f"{message.__class.__name__}:{message.id}") is None:
                await self.cache.set_object(key=f"{message.__class.__name__}:{message.id}", object=message.__dict__)
            await self.cache.add_to_list(key=f"{self.user_messages_namespace}:{user_id}", value=f"{message.__class.__name__}:{message.id}")
            
        return list_messages
      
        
        
    async def get_user_messages(self, user_id: uuid.UUID) -> List["Message"]:
    
        if messages := await self.cache.get_list(key=f"{self.user_messages_namespace}:{user_id}") is not None:
            list = []
            for message in messages:
                if cur_message := await self.cache.get_object(key=f"{message.__class.__name__}:{message.id}") is not None:
                    list.append(await self.cache.get_object(key=f"{message.__class.__name__}:{message.id}"))
                    await self.cache.update_ttl(key=f"{message.__class.__name__}:{message.id}")
                else:
                    return await self.set_messages_user_cache(user_id=user_id)
            return list
        
        return await self.set_messages_user_cache(user_id=user_id)

        

    
    
    async def add_friend(self, user: User, **criteries) -> User:
        for i in criteries:
            if i is not None:
                if friend := self.cache.get_object(key=f"{self.default_cache_namespace}:{criteries[i]}") is not None:
                    return friend
        return await self.repo.add_friend(user, **criteries)


        
            
    async def remove_friend(self, user: User, **criteries) -> User:
        for i in criteries:
            if i is not None:
                if friend := self.cache.get_object(key=f"{self.default_cache_namespace}:{criteries[i]}") is not None:
                    return friend
        return await self.repo.remove_friend(user, **criteries)
       
    
    
    async def get_received_invites(self, user: User) -> List[Invite]:
        await self.get_received_invites(user=user)
        
    async def get_sended_invites(self, user: User) -> List[Invite]:
        await self.get_sended_invites(user=user)