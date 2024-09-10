import redis.asyncio as redis
import asyncio
from config import settings
from time import sleep
from .redis_service import RedisManager
from typing import Callable
import async_timeout
from functools import partial
from .logger import log


class Broker:

    __singletone = None

    def __new__(cls, subscriber, publisher):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls)
            cls.channel_to_handler = {}
            cls.pubsub = subscriber.pubsub()
        return cls.__singletone

    def __init__(self, subscriber, publisher):
        self.subscriber = subscriber
        self.publisher = publisher
        self.channels_counter = 0

    async def publish(self, channel: str, message: str):
        try:
            log.debug(f"Start publush {channel=}\n")
            await self.publisher.publish(channel, message)
        except Exception:
            print("Я не знаю пока что не так, но что-то не так")

    async def subscribe(
        self, channel: str, handler: Callable = None, *handler_args, **handler_kwargs
    ):
        log.debug(f"Subscribe start {channel=}\n")

        if (
            channel in self.channel_to_handler
        ):  # it means that app is already subscribed to channel
            log.debug(f"{channel=} already subscribed\n")
            return

        if handler:
            log.debug("handler registrated\n")
            self.channel_to_handler[channel] = partial(handler, **handler_kwargs)

            # WARNING partial is order sensitive so if handler_args were passed they must be orderd in right way for
            # handler correct working

            await self.pubsub.subscribe(**{channel: self.channel_to_handler[channel]})
            log.debug("subscribed\n")
        else:
            self.channel_to_handler[channel] = None
            await self.pubsub.subscribe(channel)

        if self.channels_counter == 0:
            log.debug("start listen\n")
            future = asyncio.create_task(self.__listener(self.pubsub))

        self.channels_counter += 1
        log.debug(f"{self.channels_counter=}")

    async def __listener(self, channel: redis.client.PubSub):
        while True:
            try:
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    log.debug(f"(Reader) Message Received: {message}\n")
                    if message["data"] == "STOP":
                        log.debug(f"STOP WORD GET\n")
                        break
                await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
