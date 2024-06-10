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
from src.schemas.shcemas_from_db import RawDBUser
from typing import List, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from sqlalchemy.orm import DeclarativeBase
    from pydantic import BaseModel


    


class AbstractUserRepository(CRUDRepository):
    @abstractmethod
    async def get_convs(self, user_id: uuid.UUID) -> List["Conversation"]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_messages(self, user: User) -> list:
        raise NotImplementedError
    
    @abstractmethod
    async def get_user_with_messages(self):
        raise NotImplementedError
    
    @abstractmethod
    async def is_in_friend(self):
        raise NotImplementedError
    
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
    _schema = RawDBUser
    def __init__(self, repo: UserRepository, cache: AbstractCache, namespace_ttl: int, conv_schema: Type[BaseModel], message_schema: Type[BaseModel]) -> None:
        super().__init__(repo, cache, namespace_ttl)
        # will be refactored
        
        self.message_schema = message_schema
        self.conv_schema = conv_schema

    
    async def get_convs(self, user_id: uuid.UUID):
        # this cache stores only cache keys of conversation objects
        
        if convs := await self.cache.get_sets(key=f"{self.user_convs_namespace}:{user_id}") is not None:
            list = []
            for conv in convs:
                if cur_conv := await self.cache.get_object(key=conv, schema=self.conv_schema) is not None:
                    list.append(cur_conv)
                    await self.cache.update_ttl(key=f"{conv.__class.__name__}:{conv.id}")
                else:
                    return await self.__set_conv_user_cache(user_id=user_id)
            return list
        
        return await self.__set_conv_user_cache(user_id=user_id)
        
    async def get_user_messages(self, user_id: uuid.UUID) -> List[BaseModel]:
    
        if messages := await self.cache.get_sets(key=f"{self.user_messages_namespace}:{user_id}") is not None:
            list = []
            for message in messages:
                if cur_message := await self.cache.get_object(key=f"{message.__class.__name__}:{message.id}", schema=self.message_schema) is not None:
                    list.append(cur_message)
                    await self.cache.update_ttl(key=f"{message.__class.__name__}:{message.id}")
                else:
                    return await self.__set_messages_user_cache(user_id=user_id)
            return list
        
        return await self.__set_messages_user_cache(user_id=user_id)

    
    async def add_friend(self, user: User, **criteries) -> User:
        
        friend = await self.repo.add_friend(user, **criteries)
        self.cache.set_object(key=f"{self.default_cache_namespace}:{friend.id}", schema=self._schema, )
        if cur_user := self.cache.get_object(key=f"{self.default_cache_namespace}:{user.id}") is not None:
            self.cache.update_ttl(key=f"{self.default_cache_namespace}:{user.id}")

            if await self.cache.get_sets(key=f"{self.user_messages_namespace}:{user.id}") is not None:
                self.cache.add_to_set(key=f"{self.user_messages_namespace}:{user.id}", value=f"{self.default_cache_namespace}:{friend.id}")

            if await self.cache.get_sets(key=f"{self.user_messages_namespace}:{friend.id}") is not None:
                self.cache.add_to_set(key=f"{self.user_messages_namespace}:{user.id}", value=f"{self.default_cache_namespace}:{friend.id}")
        
        return friend
    

    async def remove_friend(self, user: User, **criteries) -> User:
        friend = await self.repo.remove_friend(user, **criteries)
        if cur_user := self.cache.get_object(key=f"{self.default_cache_namespace}:{user.id}") is not None:
            self.cache.update_ttl(key=f"{self.default_cache_namespace}:{user.id}")

            if await self.cache.get_sets(key=f"{self.user_messages_namespace}:{user.id}") is not None:
                self.cache.remove_from_set(key=f"{self.user_messages_namespace}:{user.id}", value=f"{self.default_cache_namespace}:{friend.id}")

            if await self.cache.get_sets(key=f"{self.user_messages_namespace}:{friend.id}") is not None:
                self.cache.remove_from_set(key=f"{self.user_messages_namespace}:{user.id}", value=f"{self.default_cache_namespace}:{friend.id}")
        
        return friend
  
       
    async def __set_conv_user_cache(self, user_id) -> List["DeclarativeBase"]: 
        list_convs = await self.repo.get_convs(user_id=user_id)
        return await self.__update_cache_for_connected_objects(obj_list=list_convs, user_id=user_id, schema=self.conv_schema, namespace=f'{self.user_convs_namespace}',)


    async def __set_messages_user_cache(self, user_id) -> List["DeclarativeBase"]:
        list_messages = await self.repo.get_user_messages(user_id=user_id)
        return await self.__update_cache_for_connected_objects(obj_list=list_messages, user_id=user_id, schema=self.message_schema, namespace=f'{self.user_messages_namespace}',)

    async def __update_cache_for_connected_objects(self, obj_list: List["DeclarativeBase"], user_id, schema: Type["BaseModel"], namespace: str):
        for obj in obj_list:
            if await self.cache.get_object(key=f"{obj.__class.__name__}:{obj.id}") is None:
                await self.cache.set_object(key=f"{obj.__class.__name__}:{obj.id}", object=obj, schema=schema)
            else:
                await self.cache.update_ttl(key=f"{obj.__class.__name__}:{obj.id}")

            await self.cache.add_to_set(key=f"{namespace}:{user_id}", value=f"{obj.__class.__name__}:{obj.id}")
            
        return obj_list
        
    

      
    
    async def get_received_invites(self, user: User) -> List[Invite]:
        await self.get_received_invites(user=user)
        
    async def get_sended_invites(self, user: User) -> List[Invite]:
        await self.get_sended_invites(user=user)