from os import name
import uuid

from sqlalchemy import select, insert, Result
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from src.crud.exceptions import RecordNotFoundError, NoEditPermissionsError
from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary, Message
from src.models.user_model import User
from typing import TYPE_CHECKING
from services.redis_service import AbstractCache
from typing import List, Type
from abc import abstractmethod
from repo_abstract import CRUDRepository, CacheCrudAlchemyRepository
from src.schemas.shcemas_from_db import RawDBConversation

if TYPE_CHECKING:
    from src.models.user_model import User
    from pydantic import BaseModel
    from sqlalchemy.orm import DeclarativeBase

class AbstractConversationRepository(CRUDRepository):
    @abstractmethod
    async def get_users(self,  conv_id: uuid.UUID, selectable: "str" = None) -> List["User"]:
        raise NotImplementedError

    @abstractmethod
    async def get_conv_messages(self, conv_id: uuid.UUID) -> List["Message"]:
        raise NotImplementedError

    @abstractmethod
    async def add_user(self,
        current_user_id: uuid.UUID,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
        permission: bool,) -> None:
        raise NotImplementedError

  


class ConversationRepository(CRUDAlchemyRepository, AbstractConversationRepository):
    _model = Conversation

    # TODO: do something with session identity map for caching
    # TODO: errors handling
    # I think that it shouldn't be async :|
    async def get_users(
        self, conv_id: uuid.UUID, selectable: "str" = None
    ) -> List["User"]:
        if selectable is None:
            selectable = User
        else:
            selectable = getattr(User, selectable)

        stmt = (
            select(selectable)
            .join(
                UserConversationSecondary,
                User.id == UserConversationSecondary.user_id,
            )
            .where(UserConversationSecondary.conversation_id == conv_id)
        )
        res = await self._session.scalars(stmt)
        res = list(res.all())
        if not res:
            raise RecordNotFoundError
        return res
    

    async def update_permissions(self, user_id: uuid.UUID, conv_id: uuid.UUID, can_edit: bool):
        stmt = (
            select(UserConversationSecondary.edit_permission)
            .where(UserConversationSecondary.conversation_id == conv_id and UserConversationSecondary.user_id == user_id)
        )
        user_conv_row = await self._session.scalar(stmt)
        if user_conv_row.edit_permission == can_edit:
            return can_edit
        user_conv_row.edit_permission = can_edit
        await self._session.commit()
        return can_edit
    
    async def delete(self, current_user_id, **crtieries):

        await self.get_permissions(
            current_user_id=current_user_id, conv_id=crtieries["id"]
        )
        return await super().delete(**crtieries)

    async def get_conv_with_admin_info(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.user_admin))
        )
        conv = await self._session.scalar(stmt)
        return conv

    # may be it will be better to make it using one querie
    # this function do it with two queries using loaded messages and thEn selecting them
    async def get_conv_messages(self, conv_id: uuid.UUID) -> List["Message"]:
        conv = await self.get_conv_with_messages(conv_id)
        return conv.messages
    
    
    # TODO: This method should'n be in interface and should be implemented in the separated service
    async def get_conv_with_messages(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.messages))
        )
        res: Result = await self._session.execute(stmt)
        conv = res.unique().scalar_one()
        return conv

    async def update(
        self,
        current_user_id,
        data,
        model_object: Conversation | None = None,
        **criteries
    ):

        if not criteries.get("id", None):
            await self.get_permissions(
                current_user_id=current_user_id, conv_id=criteries["name"]
            )
        else:
            await self.get_permissions(
                current_user_id=current_user_id, conv_id=criteries["id"]
            )
        return await super().update(data, model_object, **criteries)

    async def create(self, data: dict) -> Conversation:

        new_conv = Conversation(**data)
        new_asoc = UserConversationSecondary(edit_permission=True)
        new_conv.id = uuid.uuid4()
        new_asoc.conversation_id = new_conv.id
        new_asoc.user_id = new_conv.user_admin_fk
        self._session.add(new_conv)
        self._session.add(new_asoc)
        await self._session.commit()
        return new_conv

    async def add_user(
        self,
        current_user_id: uuid.UUID,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
        permission: bool,
    ) -> None:

        # await self.get_permissions(current_user_id=current_user_id, conv_id=conv_id)

        new_asoc = UserConversationSecondary(edit_permission=permission)
        new_asoc.conversation_id = conv_id
        new_asoc.user_id = user_id
        self._session.add(new_asoc)
        await self._session.commit()

    async def get_permissions(
        self,
        current_user_id: uuid.UUID,
        conv_id: uuid.UUID | None = None,
        name: str | None = None,
    ):
        if name and not conv_id:
            conv_id = await self._session.scalar(
                select(Conversation.id).where(Conversation.name == name)
            )
        stmt = select(UserConversationSecondary.edit_permission).where(
            UserConversationSecondary.user_id == current_user_id
            and UserConversationSecondary.conversation_id == conv_id
        )

        try:
            res: Result = await self._session.execute(stmt)
            row = res.scalar()
        except NoResultFound:
            raise RecordNotFoundError()
        if not row:
            raise NoEditPermissionsError()



class CacheConversationRepository(CacheCrudAlchemyRepository, AbstractConversationRepository):
    _schema = RawDBConversation

    def __init__(self, repo: ConversationRepository, cache: AbstractCache, namespace_ttl: int, user_schema: Type["BaseModel"], message_schema: Type["BaseModel"]) -> None:
        super().__init__(repo, cache, namespace_ttl)
        self.user_schema = user_schema
        self.message_schema = message_schema

    async def get_users(
        self, conv_id: uuid.UUID, selectable: "str" = None
    ) -> List["User" | "BaseModel"]:
        if users := await self.cache.get_sets(key=f"{self.users_in_conv_namespace}:{conv_id}") is not None:
            list = []
            for user in users:
                if cur_user := await self.cache.get_object(key=user, schema=self.user_schema) is not None:
                    list.append(cur_user)
                    await self.cache.update_ttl(key=user)
                else:
                    return await self. __set_users_in_conv_cache(conv_id=conv_id)
            return list
        
        return await self.__set_users_in_conv_cache(self, conv_id=conv_id)
    
    
    async def __set_users_in_conv_cache(self, conv_id) -> List["User"]:
        list_users = await self.repo.get_users(conv_id=conv_id)
        return await self.__update_cache_for_connected_objects(obj_list=list_users, conv_id=conv_id, schema=self.user_schema, namespace=f'{self.users_in_conv_namespace}',)


    async def __update_cache_for_connected_objects(self, obj_list: List["DeclarativeBase"], conv_id, schema: Type["BaseModel"], namespace: str):
        for obj in obj_list:
            if await self.cache.get_object(key=f"{obj.__class.__name__}:{obj.id}") is None:
                await self.cache.set_object(key=f"{obj.__class.__name__}:{obj.id}", object=obj, schema=schema)
            else:
                await self.cache.update_ttl(key=f"{obj.__class.__name__}:{obj.id}")

            await self.cache.add_to_set(key=f"{namespace}:{conv_id}", value=f"{obj.__class.__name__}:{obj.id}")
            
        return obj_list
    

    async def __set_messages_in_conv_cache(self, conv_id) -> List["Message"]:
        list_messages = await self.repo.get_conv_messages(conv_id=conv_id)
        return await self.__update_cache_for_connected_objects(obj_list=list_messages, conv_id=conv_id, schema=self.message_schema, namespace=f'{self.convs_messages_namespace}')


    async def delete(self, current_user_id, **crtieries):
        await self.get_permissions(
            current_user_id=current_user_id, conv_id=crtieries["id"]
        )
        return await super().delete(**crtieries)

    async def get_conv_messages(self, conv_id: uuid.UUID) -> List["Message"]:

        if messages := await self.cache.get_sets(key=f"{self.convs_messages_namespace}:{conv_id}") is not None:
            list = []
            for message in messages:
                if cur_message := await self.cache.get_object(key=message, schema=self.message_schema) is not None:
                    list.append(cur_message)
                    await self.cache.update_ttl(key=cur_message)
                else:
                    return await self. __set_messages_in_conv_cache(conv_id=conv_id)
            return list
        
        return await self.__set_messages_in_conv_cache(self, conv_id=conv_id)
    
    async def get_conv_with_messages(self, conv_id: uuid.UUID) -> Conversation:
        return await self.repo.get_conv_with_messages(conv_id=conv_id)

    async def update(
        self,
        current_user_id,
        data,
        model_object: Conversation | None = None,
        **criteries
    ):

        self.repo.update(current_user_id, data=data, model_object=model_object, **criteries)

    async def create(self, data: dict) -> Conversation:
        new_conv = self.repo.create(new_conv)
        await self.cache.set_object(key=f"{self.default_cache_namespace}:{new_conv.id}", schema=self._schema)
        return new_conv

    async def add_user(
        self,
        current_user_id: uuid.UUID,
        user_id: uuid.UUID,
        conv_id: uuid.UUID,
        permission: bool,
    ) -> None:
        
        await self.get_permissions(current_user_id=current_user_id, conv_id=conv_id)

        await self.repo.add_user(current_user_id=current_user_id, user_id = user_id, conv_id = conv_id, permission=permission)

        if conv := await self.cache.get_object(key=f"{self.default_cache_namespace}:{conv_id}") is not None:
            if set_of_users := await self.cache.get_sets(key=f"{self.users_in_conv_namespace}:{conv_id}") is not None:
                self.cache.add_to_set(key=f"{self.users_in_conv_namespace}:{conv_id}", value=f'{User.__class__.__name__}:{user_id}')
            if set_of_convs_in_user_cache := await self.cache.get_sets(key=f"{self.user_convs_namespace}:{user_id}") is not None:
                self.cache.add_to_set(key=f"{self.user_convs_namespace}:{user_id}", value=f'{self.default_cache_namespace}:{conv_id}')
            

    async def get_permissions(
        self,
        current_user_id: uuid.UUID,
        conv_id: uuid.UUID | None = None,
        name: str | None = None,
    ):
        if permission := await self.cache.get_dict(key=f"{self.convs_permission_namespace}", dict_key=f'{current_user_id}') is not None:
            if not int(permission):
                raise NoEditPermissionsError()
        else:
            if name and not conv_id:
                conv_id = await self._session.scalar(
                    select(Conversation.id).where(Conversation.name == name)
                )
            stmt = select(UserConversationSecondary.edit_permission).where(
                UserConversationSecondary.user_id == current_user_id
                and UserConversationSecondary.conversation_id == conv_id
            )

            try:
                res: Result = await self._session.execute(stmt)
                permission = res.scalar()
                permission_in_cache = 1 if permission else 0
                self.cache.set_dict(key=f"{self.convs_permission_namespace}", dict_key=f'{current_user_id}', dict_value=permission)
            except NoResultFound:
                raise RecordNotFoundError()
        if not permission:
            raise NoEditPermissionsError()