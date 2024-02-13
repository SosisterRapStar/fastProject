import asyncio

from src.crud.demo_relational_crud import get_user_convs

# from src.crud.conversation_crud import *
from src.crud.user_crud import *
from src.crud.utils import get_object
from src.models import db_handler


#
async def main():
    async with db_handler.session() as ses:
        a = await get_object(async_session=ses, model=User, id="9f3454e3-e6c3-4501-809f-c8a38ceef2ed")
        print(a)


if __name__ == "__main__":
    asyncio.run(main())
