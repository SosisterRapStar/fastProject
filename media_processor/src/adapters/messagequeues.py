from aiokafka import AIOKafkaConsumer, ConsumerRecord  # type: ignore
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Callable, Coroutine
from config import settings, logger  # type: ignore
import asyncio
from typing import Dict
from src.services.video_compressor import video_compressing_pipeline
from src.services.S3service import send_files_to_S3
from src.services.kafka_service import send_event_to_kafka
from src.services.deduplicator import deduplicate_files
from src.services.filer_deleter import delete_files
from src.domain.events import (
    Event,
    Command,
    CheckDuplicates,
    ProcessNewFileFromClient,
    AtachmentProcessed,
    AtachmentUploadedToS3,
    DeleteProcessedFilesFromLocalStorage,
    DeleteAlreadyExistedFile,
)


@dataclass
class BaseConsumerByTopic(ABC):
    """
    Base class for kafka consumer class

    Raises:
        NotImplementedError: _description_
        NotImplementedError: _description_
        NotImplementedError: _description_
    """

    @abstractmethod
    async def start(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def stop(self):
        raise NotImplementedError

    @abstractmethod
    async def start_consume(self, topics: list[str], callback: Callable) -> None:
        raise NotImplementedError


@dataclass
class BaseQueue(ABC):
    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def stop(self):
        raise NotImplementedError

    @abstractmethod
    async def consume(self):
        raise NotImplementedError


EventHandler = Callable[[Event, asyncio.Queue], None]
CommandHandler = Callable[[Command, asyncio.Queue], None]


async def handle_event(
    event: Event, queue: asyncio.Queue
):  # одно событие могут быть обработаны множеством функций
    HANDLERS: Dict[Event, EventHandler] = {
        AtachmentProcessed: [send_files_to_S3],
        AtachmentUploadedToS3: [send_event_to_kafka],
    }
    for handler in HANDLERS[type(event)]:
        future = asyncio.create_task(handler(event, queue))


async def handle_command(
    command: Command, queue: asyncio.Queue
):  # команды могут быть обработаны только одной конкретной функцией
    HANDLERS: Dict[Command, CommandHandler] = {
        CheckDuplicates: deduplicate_files,
        ProcessNewFileFromClient: video_compressing_pipeline,
        DeleteProcessedFilesFromLocalStorage: delete_files,
        DeleteAlreadyExistedFile: delete_files,
    }
    handler = HANDLERS[type(command)]
    fiture = asyncio.create_task(handler(command, queue))


@dataclass
class AsyncioConsumer:
    queue: asyncio.Queue = asyncio.Queue()

    async def start(self) -> None:
        asyncio.create_task(self.consume())

    async def stop(self):
        await self.queue.put("")

    async def consume(self):
        logger.debug("Consumer started\n")
        while True:
            message = await self.__queue.get()

            if isinstance(message, Event):
                logger.debug(f"Got event: {message}\n")
                await handle_event(event=message, queue=self.queue)

            elif isinstance(message, Command):
                logger.debug(f"Got command: {message}\n")
                await handle_command(command=message, queue=self.queue)

            else:
                logger.debug(f"Got something else  - stop\n")
                break


@dataclass
class BaseProducer(ABC):
    pass


class KafkaProducer(BaseProducer):
    pass


@dataclass
class KafkaConsumer(BaseConsumerByTopic):
    """
    Incapsulates logic of AIOKafkaConsumer
    """

    _consumer: AIOKafkaConsumer

    async def start(self) -> None:
        logger.debug("Kafka consumer was inited")
        await self._consumer.start()

    async def stop(self) -> None:
        logger.debug("Kafka consumer was stopped")
        await self._consumer.stop()

    async def start_consume(self, topics: list[str], callback: Callable) -> None:
        try:
            self._consumer.subscribe(topics=topics)
            logger.debug(f"Kafka subscribed to {topics}")
        except Exception as e:
            logger.error(f"Error occured duriong subscribing {e}")
            raise e

        try:
            logger.debug("Kafka started listening loop")
            await self._consume_loop(callback)
        except Exception as e:
            logger.error("Error during consumering {e}")

        finally:
            await self.stop()

    async def _consume_loop(self, callback: Callable):
        """_summary_
        Provides a loop for consume data
        """
        async for msg in self._consumer:
            try:
                msg = await decoder(msg)
                await callback(msg)
            except Exception as e:
                logger.error(
                    f"Error occured during message decoding or in callback func {e}"
                )


async def decoder(msg: ConsumerRecord):
    # try:
    #     decoded_message = msg.value.decode("utf-8")
    #     return msg
    # except UnicodeDecodeError as e:
    #     print("Failed to decode message as UTF-8")
    #     raise e
    print("key={} value={}".format(msg.key, msg.value))
