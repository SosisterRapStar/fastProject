from aiokafka import AIOKafkaConsumer, ConsumerRecord, AIOKafkaProducer  # type: ignore
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from typing import Callable, Coroutine
from config import logger  # type: ignore


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
class BaseProducer(ABC):
    @abstractmethod
    async def start(self):
        raise NotImplementedError

    @abstractmethod
    async def send(self, topic: str, value: bytes):
        raise NotImplementedError


@dataclass
class FakeProducer(BaseProducer):
    sended_messages: list = field(default_factory=list)

    async def start(self):
        return 1

    async def send(self, topic: str, value: bytes):
        self.sended_messages.append(value)
        return self.sended_messages


@dataclass
class KafkaProducer(BaseProducer):
    _producer: AIOKafkaProducer

    async def start(self):
        await self._producer.start()

    async def send(self, topic: str, value: bytes):
        await self._producer.send(topic=topic, value=value)


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
    try:
        decoded_message = msg.value.decode("utf-8")
        return msg
    except UnicodeDecodeError as e:
        print("Failed to decode message as UTF-8")
        raise e
    print("key={} value={}".format(msg.key, msg.value))
