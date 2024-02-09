import asyncio
from src.crud.conversation_crud import *
from src.crud.user_crud import *

#
async def main():
    async with db_handler.session() as ses:
        user = await load_user_with_convs(async_session=ses, user_id=uuid.UUID("9f3454e3-e6c3-4501-809f-c8a38ceef2ed"))
        print(user.conversations)
if __name__ == "__main__":
    asyncio.run(main())
