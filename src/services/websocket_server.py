from .logger import log
from json import JSONDecodeError
from typing import TYPE_CHECKING
from services.message_handlers import chat_message_handler
from src.models.base import db_handler
from starlette.websockets import WebSocketDisconnect
from crud.message_repository import MessageRepository


if TYPE_CHECKING:
    from .connection_manager import ConnectionManager
    from .broker_service import Broker
    from .connection_manager import ChatService
    from fastapi import WebSocket
    from src.models.user_model import User


async def start_server(
    manager: "ConnectionManager",
    current_user: "User",
    websocket: "WebSocket",
    broker: "Broker",
    chat: "ChatService",
):
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except JSONDecodeError as e:
                log.error("WTF DUDE !!!!")
            log.debug(f"{current_user.name=} start subscribe")
            log.debug(f"{broker=}")
            await broker.subscribe(
                channel=data["conv_id"], handler=chat_message_handler, chat=chat
            )
            messageToSaveInDb = {
                "conversation_fk": data["conv_id"],
                "content": data["message"],
                "user_fk": current_user.id,
            }
            session = db_handler.get_scoped_session()
            async with session() as session:
                message_repo = MessageRepository(session=session)
                await message_repo.create(messageToSaveInDb)
            messageForUsersAndOtherServers = f"""
            {{
            "conversation_id": "{data["conv_id"]}",
            "user_name": "{current_user.name}",
            "content": "{data["message"]}"
            }}
            """
            await broker.publish(
                channel=data["conv_id"], message=messageForUsersAndOtherServers
            )

    except WebSocketDisconnect:
        await manager.disconnect(user_id=current_user.id, websocket=websocket)
