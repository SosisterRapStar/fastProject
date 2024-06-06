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
from typing import List
from abc import abstractmethod
from repo_abstract import CRUDRepository

if TYPE_CHECKING:
    from src.models.user_model import User


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

        await self.get_permissions(current_user_id=current_user_id, conv_id=conv_id)

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