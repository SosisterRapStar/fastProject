from adapters.messagequeues import AsyncioConsumer
from typing import Annotated
from fastapi import Depends


async def get_async_cons() -> AsyncioConsumer:
    return AsyncioConsumer()


asyncio_consumer = Annotated[AsyncioConsumer, Depends(get_async_cons)]
