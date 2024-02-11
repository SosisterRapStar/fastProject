import asyncio

from src.crud.demo_relational_crud import get_user_convs
# from src.crud.conversation_crud import *
from src.crud.user_crud import *
from src.models import db_handler


#
async def main():
    async with db_handler.session() as ses:
if __name__ == "__main__":
    asyncio.run(main())
