import asyncio



from src.crud.demo_relational_crud import get_user_convs

# from src.crud.conversation_crud import *
from src.crud.user_crud import *
from src.crud.utils import get_object
from src.models import db_handler
from src.models.chat_models import Conversation, UserConversationSecondary


#
async def main():
    async with db_handler.session() as ses:
        stmt = (
            select(Conversation)
            .join(UserConversationSecondary, Conversation.id == UserConversationSecondary.conversation_id)
            .join(User, User.id == UserConversationSecondary.user_id)
            .where(User.name == "")
        )
        res = await ses.scalars(stmt)
        a = list(res.all())[0]
        print(a.user_admin_fk)
        print(stmt)


if __name__ == "__main__":
    asyncio.run(main())
