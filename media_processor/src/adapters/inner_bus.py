from dataclasses import dataclass
from typing import Callable
from config import logger  # type: ignore
import asyncio
from typing import Dict, List


from src.services.file_processor import FileProcessor
from src.services.S3service import SendToS3Handler
from src.services.kafka_service import KafkaHandler
from src.services.deduplicator import DeduplicateHandler
from src.services.file_deleter import DeleteFilesHandler

from src.domain.events import (
    Event,
    Command,
    CheckDuplicates,
    ProcessVideoFileFromClient,
    ProcessImageFileFromClient,
    AttachmentProcessed,
    AttachmentUploadedToS3,
    DeleteFilesFromLocalStorage,
    ErrorEvent,
)

EventHandler = Callable[[Event, asyncio.Queue], None]
CommandHandler = Callable[[Command, asyncio.Queue], None]


RAW_EVENT_HANDLERS: Dict[Event, List[EventHandler]] = {
    AttachmentProcessed: [
        SendToS3Handler,
    ],
    AttachmentUploadedToS3: [
        KafkaHandler,
    ],
}


RAW_COMMAND_HANDLERS: Dict[Command, CommandHandler] = {
    CheckDuplicates: DeduplicateHandler,
    ProcessVideoFileFromClient: FileProcessor,
    ProcessImageFileFromClient: FileProcessor,
    DeleteFilesFromLocalStorage: DeleteFilesHandler,
}


@dataclass
class AsyncioConsumer:
    command_handlers: Dict[Command, CommandHandler]
    event_handlers: Dict[Event, List[EventHandler]]
    queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> asyncio.Task:
        future = asyncio.create_task(self.consume())
        return future

    async def handle_event(
        self, event: Event, queue: asyncio.Queue
    ):  # одно событие может быть обработано множеством функций
        for handler in self.event_handlers[type(event)]:
            future = asyncio.create_task(handler(event, queue))

    async def handle_command(
        self, command: Command, queue: asyncio.Queue
    ):  # команды могут быть обработаны только одной конкретной функцией
        handler = self.command_handlers[type(command)]
        fiture = asyncio.create_task(handler(command, queue))

    async def stop(self):
        await self.queue.put("")

    async def consume(self):
        logger.debug("Consumer started\n")
        while True:
            message = await self.queue.get()

            if isinstance(message, Event):
                logger.debug(f"Got event: {message}\n")
                await self.handle_event(event=message, queue=self.queue)

            elif isinstance(message, Command):
                logger.debug(f"Got command: {message}\n")
                await self.handle_command(command=message, queue=self.queue)

            else:
                logger.debug(f"Got something else  - stop\n")
                break
