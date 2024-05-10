import redis.asyncio as redis
import asyncio 
from config import settings
from time import sleep
from .redis_service import RedisManager
from abc import ABC, abstractmethod
from typing import Callable
import async_timeout




class Broker:
    
    __singletone = None


    def __new__(cls, subscriber, publisher):
        if cls.__singletone is None:
            cls.__singletone = super().__new__(cls)
        return cls.__singletone

    def __init__(self, subscriber, publisher):
        self.subscriber = subscriber
        self.publisher = publisher
        self.pubsub = self.subscriber.pubsub()
        self.channels_counter = 0
        
            
    async def publish(self, channel: str, message: str):
        try: 
            await self.publisher.publish(channel, message)
        except Exception:
            print("Я не знаю пока что не так, но что-то не так") 
    
    async def subscribe(self, channel: str, handler: Callable = None):
       
        if handler:
            await self.pubsub.subscribe(**{channel: handler})
        else:
            await self.pubsub.subscribe(channel)
            
        if self.channels_counter == 0:
            future = asyncio.create_task(self.__listener(self.pubsub))
        self.channels_counter += 1
            
    
    async def __listener(self, channel: redis.client.PubSub):
        while True:
            try:
            
                message = await channel.get_message(ignore_subscribe_messages=True)
                if message is not None:
                    print(f"(Reader) Message Received: {message}")
                    if message["data"] == "STOP":
                        print("(Reader) STOP")
                        break
                await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass
                


    

        
