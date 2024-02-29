import uuid

from sqlalchemy import select, insert, Result
from sqlalchemy.orm import joinedload

from src.crud.exceptions import RecordNotFoundError
from src.crud.repo_abstract import CRUDAlchemyRepository
from src.models.chat_models import Conversation, UserConversationSecondary, Message
from src.models.user_model import User


class ConversationRepository(CRUDAlchemyRepository):
    _model = Conversation

    # TODO: do something with session identity map for caching
    # TODO: errors handling

    async def get_users(self, conv_id: uuid.UUID) -> list["User"]:
        stmt = (
            select(User)
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

    async def get_conv_with_admin_info(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.user_admin))
        )
        conv = await self._session.scalar(stmt)
        return conv

    # may be it will be better to make it using one querie
    # this function do it with two queries using loaded messages and than selecting them
    async def get_conv_messages(self, conv_id: uuid.UUID) -> list["Message"]:
        conv = await self.get_conv_with_messages(conv_id)
        return conv.messages

    async def get_conv_with_messages(self, conv_id: uuid.UUID) -> Conversation:
        stmt = (
            select(Conversation)
            .where(Conversation.id == conv_id)
            .options(joinedload(Conversation.messages))
        )
        res: Result = await self._session.execute(stmt)
        conv = res.unique().scalar_one()
        return conv

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

    async def add_user(self, user_id: uuid.UUID, conv_id: uuid.UUID,
                       permission: bool) -> None:
        # stmt = (select(UserConversationSecondary.edit_permission).
        #         where(UserConversationSecondary.user_id == user_editor_id))
        #
        # is_editor = await self._session.scalar(stmt)
        #
        # if not is_editor:
        #     raise RecordNotFoundError

        new_asoc = UserConversationSecondary(edit_permission=permission)
        new_asoc.conversation_id = conv_id
        new_asoc.user_id = user_id
        self._session.add(new_asoc)
        await self._session.commit()
