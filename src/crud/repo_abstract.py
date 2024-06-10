from abc import ABC, abstractmethod
from typing import Type

from pydantic import BaseModel
from typing import Callable, Coroutine
from typing_extensions import Unpack
from sqlalchemy.ext.asyncio import AsyncSession
from src.crud.utils import get_object, NameOrId, update_object, delete_obj
from src.models import Base
from src.services.redis_service import AbstractCache
from redis.asyncio import Redis

class CRUDRepository(ABC):

    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def get(self, **criteries):
        raise NotImplementedError

    # @abstractmethod
    # async def get_all(self):
    #     raise NotImplementedError

    @abstractmethod
    async def update(self, data: dict, **criteries):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **criteries):
        raise NotImplementedError


class CRUDAlchemyRepository(CRUDRepository):
    _model: Type[Base] = None
    
    def get_model_name(self):
        return str(self._model.__name__)

    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Base:
        # TODO: переработать работу с сессией
        new_obj = self._model(**data)
        self._session.add(new_obj)

        await self._session.commit()
        return new_obj

    async def get(self, **criteries: Unpack[NameOrId | None]) -> Base:
        
        res = await get_object(
            async_session=self._session,
            model=self._model,
            **criteries,
        )
        
        return res

    async def update(
        self,
        data: dict,
        model_object: Base | None = None,
        **criteries: Unpack[NameOrId],
    ):
        updated = await update_object(
            async_session=self._session,
            model=self._model,
            data=data,
            model_object=model_object,
            **criteries,
        )

        await self._session.commit()
        return updated

    async def delete(
        self,
        model_object: Base | None = None,
        **criteries: Unpack[NameOrId],
    ) -> None:
        returned_id = await delete_obj(
            async_session=self._session,
            model_obj=model_object,
            model=self._model,
            **criteries,
        )
        await self._session.commit()
        return returned_id


class CacheCrudAlchemyRepository(CRUDRepository):
    _schema: Type[BaseModel] = None
      # will be refactored
    

    def __init__(self, repo: CRUDAlchemyRepository, cache: AbstractCache, namespace_ttl: int) -> None:
        self.repo = repo
        self.cache = cache
        # I know it looks like shit
        # maybe create it like class var
        self.default_cache_namespace = f"{self.repo.get_model_name()}"
        self.cache.set_ttl_for_namespace(key=f"{self.default_cache_namespace}:id") # method set_ttl cuts all symbols after the last : 
        # so set_ttl for user:manager:list:1234 will be parsed to user->manager->list 
        self.users_in_conv_namespace = f"{self.default_cache_namespace}:users"
        self.convs_messages_namespace = f"{self.default_cache_namespace}:messages"
        self.convs_permission_namespace = f"{self.default_cache_namespace}:permissions"
    
        self.cache.set_ttl_for_namespace(f"{self.convs_messages_namespace}:id", ttl=500)  
        self.cache.set_ttl_for_namespace(f"{self.users_in_conv_namespace }:id", ttl=500)
        self.cache.set_ttl_for_namespace(f"{self.convs_permission_namespace}:id", ttl=500)
        
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

        
    async def create(self, data: dict):
        obj = await self.repo.create(data=data)
        await self.cache.set_object(key=f"{self.default_cache_namespace}:{obj.id}", object=obj, schema=self._schema)
        return obj
    
    async def delete(self,
        model_object: Base | None = None,
        **criteries: Unpack[NameOrId]):
        
        id = await self.repo.delete(model_object, **criteries)
        if await self.cache.get_object(key=f"{self.default_cache_namespace}:{model_object.id}") is not None:
            await self.cache.delete_key(key=f"{self.default_cache_namespace}:{id}")
        return id
    
    async def update( self,
        data: dict,
        model_object: Base | None = None,
        **criteries: Unpack[NameOrId],):
        
        updated = await self.repo.update(data, model_object, **criteries)
        self.cache.set_object(key=f"{self.default_cache_namespace}:{updated.id}", object=updated, schema=self._schema)
        return updated
        
    
    async def get(self, **criteries: Unpack[NameOrId | None]):
        if 'name' not in criteries and 'id' not in criteries:
            return await self.repo.get(**criteries)
        
        for key in criteries:
            if value := criteries[key]:
                if cached := await self.cache.get_object(key=f"{self.default_cache_namespace}:{value}") is not None:
                    return cached
                else:
                    obj = await self.repo.get(**criteries)
                    await self.cache.set_object(key=f"{self.default_cache_namespace}:{value}", object=obj.__dict__)
                    return obj
        
        

        
    